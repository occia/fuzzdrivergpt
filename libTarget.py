import copy
import os
import pickle
import re
from pathlib import Path

try:
	import yaml
except Exception as ex:
	print('[WARN] package yaml not found, assume we are in the container header/validation stage, keep execution')

class TargetCfg:

	def __init__(self, cfgs=None, build_cfgs_yml=None, target=None, task_idx=None, basedir='.', workdir=None):
		#
		# task_idx is used for unique naming in parallel scenario
		#
		# load build cfgs
		if (cfgs != None and build_cfgs_yml != None) or (cfgs == None and build_cfgs_yml == None):
			raise Exception('error constructor usage for TargetCfg')

		if cfgs != None:
			self.cfgs = cfgs
			if target == None:
				raise Exception('missing target for directly passing cfg construction')

		else:
			with open(build_cfgs_yml, 'r') as f:
				build_cfgs = yaml.safe_load(f)
				#print(build_cfgs)
				self.cfgs = build_cfgs['targets'][target]

		self.language = self.cfgs['language'].lower()
		self.target = target
		self.basedir = os.path.abspath(basedir)
		if workdir == None:
			self.workdir = os.path.join(self.basedir, 'targets', self.target, self.language, ('para-%s' % (str(task_idx))) if task_idx != None else 'solo')
		else:
			self.workdir = workdir
		self.cachedir = os.path.join(self.basedir, 'targets', self.target, self.language, 'cache')

		self.apiblocklist = self.cfgs['apiblocklist']
		self.headers = self.get_header_files(self.cfgs['headers'])
		self.binaries = self.cfgs['binaries']
		self.imagename = self.cfgs['image']
		self.precode = eval('"""' + self.cfgs['precode'] + '"""')

		if self.language == 'c' or self.language == 'cpp':
			if 'autoinclude' not in self.cfgs:
				self.autoinclude = True
			else:
				self.autoinclude = self.cfgs['autoinclude']

		if self.language == 'c':
			self.outfile = os.path.join(self.workdir, 'dummyfuzzer.c')
			self.testfile = os.path.join(self.workdir, 'dummytester.c')
		elif self.language == 'cpp':
			self.outfile = os.path.join(self.workdir, 'dummyfuzzer.cc')
			self.testfile = os.path.join(self.workdir, 'dummytester.cc')
		else:
			raise Exception('unsupported language %s for target %s' % (self.language, self.target))

		self.validatepickle = os.path.join(self.workdir, 'validate.pickle')
		self.statusfile = os.path.join(self.workdir, 'status.txt')
		self.outexe = os.path.join(self.workdir, 'dummyfuzzer')
		self.logfile = os.path.join(self.workdir, 'build.log')
		self.fuzzlog = os.path.join(self.workdir, 'fuzz.log')
		self.artifactdir = os.path.join(self.workdir, 'artifact')
		self.seeddir = os.path.join(self.workdir, 'seeds')

		self.headerpickle = os.path.join(self.workdir, 'header.pickle')
		self.headerparampickle = os.path.join(self.workdir, 'headerparam.pickle')
		self.queryfile = os.path.join(self.workdir, 'input_queries.json')

		self.apicachepickle = os.path.join(self.cachedir, 'apicache.pickle')

		self.compileopts = self.cfgs['compile']
		# we do not care this
		self.compileopts.append('-Wno-unused-variable')
		self.compileopts.append('-Wno-newline-eof')
		self.compileopts.append('-Wno-unused-but-set-variable')
		# we shift this to linker error
		self.compileopts.append('-Wno-implicit-function-declaration')
		self.buildcmd = self.cfgs['build'].replace('COMPBASE' ,' '.join(self.compileopts)).replace('OUTFILE', self.outfile).replace('OUTEXE', self.outexe)

		if 'compile_cpp' in self.cfgs and 'build_cpp' in self.cfgs:
			self.compileopts_cpp = self.cfgs['compile_cpp']
			# we do not care this
			self.compileopts_cpp.append('-Wno-unused-variable')
			self.compileopts_cpp.append('-Wno-newline-eof')
			self.compileopts_cpp.append('-Wno-unused-but-set-variable')
			# we shift this to linker error
			self.compileopts_cpp.append('-Wno-implicit-function-declaration')
			self.buildcmd_cpp = self.cfgs['build_cpp'].replace('COMPBASE' ,' '.join(self.compileopts_cpp)).replace('OUTFILE', self.outfile).replace('OUTEXE', self.outexe)

		self.runcmd = self.cfgs['run'].replace('OUTEXE', self.outexe).replace('ARTIFACTDIR', self.artifactdir).replace('SEEDDIR', self.seeddir)
		self.fuzzsh = "/tmp/fuzz.sh"
		#self.runcmd_subprocess = self.runcmd.split()
		self.runcmd_subprocess = [ "bash", "-x", "/tmp/fuzz.sh" ]

		self.testcase = os.path.join(self.workdir, 'testcase')
		self.sgusagejson = os.path.join(self.workdir, 'sgusage.json')
		self.testexe = os.path.join(self.workdir, 'dummytester')
		self.testlog = os.path.join(self.workdir, 'test.log')
		self.testbuildcmd = self.cfgs['build'].replace('COMPBASE' ,' '.join(self.compileopts)).replace('OUTFILE', self.testfile).replace('OUTEXE', self.testexe).replace('-fsanitize=fuzzer-no-link', '').replace('-fsanitize=fuzzer', '')

		self.known_drivers = self.cfgs['known_drivers']

	def getOutTreeBuildCmd(self, outfile, outexe):
		return self.cfgs['build'].replace('COMPBASE' ,' '.join(self.compileopts)).replace('OUTFILE', outfile).replace('OUTEXE', outexe)

	def getOutTreeBuildCmdCpp(self, outfile, outexe):
		return self.cfgs['build_cpp'].replace('COMPBASE' ,' '.join(self.compileopts_cpp)).replace('OUTFILE', outfile).replace('OUTEXE', outexe)

	@staticmethod
	def pickleTo(frm, picklepath):
		obj = copy.deepcopy(frm)
		obj.docker = None
		with open(picklepath, 'wb') as f:
			pickle.dump(obj, f)

	@staticmethod
	def pickleFrom(to):
		with open(to, 'rb') as f:
			obj = pickle.load(f)
			obj.headers = obj.get_header_files(obj.cfgs['headers'])
			return obj

	def get_header_files(self, header_dict):
		files = {}

		for prefix, pattern in header_dict.items():
			absprefix = str(Path(prefix).resolve())
			for p in Path(prefix).glob(pattern):
				if p.is_file():
					absfile = p.resolve()
					absfile = str(absfile)
					#print('absfile %s' % (absfile))
					if absfile in files:
						#pick the most specific prefix if there is one more prefix for this file
						if len(files[absfile]) < len(absprefix):
							files[absfile] = absprefix
					else:
						files[absfile] = absprefix

		return files
