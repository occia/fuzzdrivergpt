import os
import re
import sys
import json
import shutil
import subprocess

import clang.cindex

from libTarget import TargetCfg

from validation import libSemanticChecker
from validation import libVR

class BaseValidator:

	def __init__(self, cfg):
		self.cfg = cfg
		if not os.path.exists(self.cfg.workdir):
			os.makedirs(self.cfg.workdir, exist_ok=True)
		self.reset()

	def del_if_exist(self, filename):
		if os.path.exists(filename):
			os.remove(filename)

	def reset(self):
		self.process = None
		self.status = { 
			'build_cmd': self.cfg.buildcmd,
			'run_cmd': self.cfg.runcmd,
			'vali_phase': 'init',
			"vali_result": libVR.UncheckedVR().toJSON(),
			"vali_detail": None,
		}
		self.del_if_exist(self.cfg.statusfile)
		self.del_if_exist(self.cfg.outfile)
		self.del_if_exist(self.cfg.outexe)
		self.del_if_exist(self.cfg.logfile)
		self.del_if_exist(self.cfg.fuzzlog)
		if os.path.exists(self.cfg.artifactdir):
			shutil.rmtree(self.cfg.artifactdir, ignore_errors=True)
		if os.path.exists(self.cfg.seeddir):
			shutil.rmtree(self.cfg.seeddir, ignore_errors=True)

	def sync_statusfile(self):
		with open(self.cfg.statusfile, 'w') as f:
			json.dump(self.status, f)

	def update_code(self, code):
		with open(self.cfg.outfile, 'w') as f:
			f.write(code)

	def update_test_code(self, code):
		with open(self.cfg.testfile, 'w') as f:
			f.write(code)

	def show_code(self):
		if not os.path.exists(self.cfg.outfile):
			return None

		with open(self.cfg.outfile, 'r') as f:
			return f.read(-1)

	def show_test_code(self):
		if not os.path.exists(self.cfg.testfile):
			return None

		with open(self.cfg.testfile, 'r') as f:
			return f.read(-1)

	def show_fuzz_result(self):
		if not os.path.exists(self.cfg.fuzzlog):
			return None

		with open(self.cfg.fuzzlog, 'rb') as f:
			raw_fuzzlog = None
			try:
				raw_fuzzlog = f.read(-1)

			except MemoryError as me:
				return 'log file corrupted with memory error'

			fuzzlog = raw_fuzzlog.decode('utf-8', errors='ignore')
			return fuzzlog

	def text_truncation(self, query_result):
		global sig

		self.update_code(query_result)

		# currently no extra handling of the code
		try:
			oldpwd = os.getcwd()
			os.chdir(self.cfg.basedir)

			index = clang.cindex.Index.create()
			tu = index.parse(self.cfg.outfile, self.cfg.compileopts)
			root = tu.cursor

			os.chdir(oldpwd)

		except Exception as ex:
			print('parsing error during text_truncation %s' % (ex)) 
			os.chdir(oldpwd)

			self.status['error_detected'] = True
			self.status['vali_phase'] = 'text_truncation'
			self.status['vali_result'], self.status["vali_detail"] = libVR.ExpCorrErrVR.build(ex)
			return

		# find the range of the key function
		func_end_line, func_end_column = None, None
		for child in root.get_children():
			# the func is written in our fuzz driver
			if str(child.location.file) == self.cfg.outfile:
				#if child.kind == clang.cindex.CursorKind.UNEXPOSED_DECL or child.kind == clang.cindex.CursorKind.LINKAGE_SPEC:
				#	# the LLVMFuzzerTestOneInput is started with extern
				#	key_node = None
				#	for grandchild in child.get_children():
				#		if grandchild.kind == clang.cindex.CursorKind.FUNCTION_DECL and grandchild.mangled_name == 'LLVMFuzzerTestOneInput':
				#			key_node = grandchild
				#			break
				#	if key_node != None:
				#		# found the first LLVMFuzzerTestOneInput func
				#		func_end = key_node.extent.end.line
				#		break

				if child.kind == clang.cindex.CursorKind.FUNCTION_DECL and child.mangled_name == 'LLVMFuzzerTestOneInput':
					# found the first LLVMFuzzerTestOneInput func
					#help(child.extent)
					#print(child.extent.end.file)
					#print(child.extent.start.line)
					#print(child.extent.start.column)
					#print(child.extent.start.offset)
					#print(child.extent.end.line)
					#print(child.extent.end.column)
					#print(child.extent.end.offset)
					#func_end = child.extent.end.offset
					func_end_line = child.extent.end.line
					func_end_column = child.extent.end.column - 1
					break
		
		print('build command: %s' % (self.cfg.buildcmd))
		#print('length of query_result is %s' % (len(query_result)))
		print('func_end_line/column is %s/%s' % (func_end_line, func_end_column))

		if func_end_line == None:
			# the query result is corrupted to be parsed
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'text_truncation'
			self.status['vali_result'], self.status["vali_detail"] = libVR.NoFuncCorrErrVR.build()
			return

		lines = query_result.split('\n')
		truned_lines = []
		for lineno in range(len(lines)):
			if lineno <= func_end_line - 1:
				truned_lines.append(lines[lineno])
			elif lineno == func_end_line - 1:
				truned_lines.append(lines[lineno][:func_end_column])

		if truned_lines[-1][-1] != '}':
			# this is a corrupted function (TODO: we didnt consider/test the case that functions are defined using macro)
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'text_truncation'
			self.status['vali_result'], self.status["vali_detail"] = libVR.IncompleteFuncCorrErrVR.build()
			return

		# shrink the query result to the end of the func
		print('before truncation, code:\n======\n%s\n' % (query_result))
		code = '\n'.join(truned_lines)
		if re.search('%s\(' % (sig), code) == None:
			# TODO: this is a rough measure for checking whether the api has been called or not, replace this when we have static analysis ability
			# api is not used in this fuzz driver
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'text_truncation'
			self.status['vali_result'], self.status["vali_detail"] = libVR.NOAPICorrErrVR.build()
			return

		self.update_code(code)
		print('======\nafter truncation, code:\n======\n%s\n' % (code))

		self.status['error_detected'] = False
		self.status['vali_phase'] = 'text_truncation'
		self.status['vali_result'], self.status["vali_detail"] = libVR.PartlyCheckedVR.build("Code has been truncated")
		return

	def check_compile(self):
		try:
			oldpwd = os.getcwd()
			os.chdir(self.cfg.basedir)

			index = clang.cindex.Index.create()
			print('self.cfg.compileopts %s' % (self.cfg.compileopts))
			tu = index.parse(self.cfg.outfile, self.cfg.compileopts)
			root = tu.cursor

			os.chdir(oldpwd)
		
		except Exception as ex:
			print('parsing error during check_compile %s' % (ex)) 
			os.chdir(oldpwd)

			self.status['error_detected'] = True
			self.status['vali_phase'] = 'compile'
			self.status['vali_result'], self.status["vali_detail"] = libVR.ExpCorrErrVR.build(ex)
			return

		for diag in tu.diagnostics:
			if diag.severity == diag.Error or diag.severity == diag.Fatal:
				# only the first diagnostics

				print(diag.severity)
				print(diag.category_name)
				print(diag.spelling)
				print(diag)
				#print('------')
				#print(diag.location)
				##print(diag.ranges)
				##print(diag.fixits)
				#print(diag.location.file)
				#print(self.cfg.outfile)
				#print(diag.location.line)
				#print(diag.location.offset)
				#print(diag.location.column)
				##help(diag.ranges)
				##help(diag.fixits)
				##print(help(tu))

				# return 1st error
				self.status['error_detected'] = True
				self.status['vali_phase'] = 'compile'
				self.status['vali_result'], self.status["vali_detail"] = libVR.ParseErrVR.build(diag, self.cfg.outfile)
				return
		
		self.status['error_detected'] = False
		self.status['vali_phase'] = 'compile'
		self.status['vali_result'], self.status["vali_detail"] = libVR.PartlyCheckedVR.build('Compile check has passed')
		return

	def check_link(self):
		global sig

		oldpwd = os.getcwd()
		os.chdir(self.cfg.basedir)

		# TODO: dirty hack
		ret = None
		if self.cfg.target == 'igraph' and sig == 'igraph_automorphism_group':
			code = self.show_code()
			code = code.replace('extern int LLVMFuzzerTestOneInput', 'extern "C" int LLVMFuzzerTestOneInput')
			self.update_code(code)

			print('build command cpp: %s' % (self.cfg.buildcmd_cpp))
			ret = os.system(self.cfg.buildcmd_cpp + " 1> " + self.cfg.logfile + " 2>&1")
		else:
			print('build command: %s' % (self.cfg.buildcmd))
			ret = os.system(self.cfg.buildcmd + " 1> " + self.cfg.logfile + " 2>&1")

		os.chdir(oldpwd)

		if ret != 0:
			with open(self.cfg.logfile, 'r') as f:
				#print(f.read(-1))
				self.status['error_detected'] = True
				self.status['vali_phase'] = 'link'
				self.status['vali_result'], self.status["vali_detail"] = libVR.LinkErrVR.build(f.read(-1))
				return

		self.status['error_detected'] = False
		self.status['vali_phase'] = 'link'
		self.status['vali_result'], self.status["vali_detail"] = libVR.PartlyCheckedVR.build('Link check has passed')
		return

	def check_by_semantic_tester(self, checker):
		# do check when we have a checker
		code = self.show_code()
		test_code = checker.gen_test_code(code)
		self.update_test_code(test_code)

		# compile the modified fuzz driver
		oldpwd = os.getcwd()
		os.chdir(self.cfg.basedir)

		print('semantic test build command: %s' % (self.cfg.testbuildcmd))
		ret = os.system(self.cfg.testbuildcmd + " 1> " + self.cfg.testlog + " 2>&1")

		os.chdir(oldpwd)

		if ret != 0:
			# error
			log = None
			with open(self.cfg.testlog, 'rb') as f:
				try:
					raw_log = f.read(-1)
					log = raw_log.decode('utf-8', errors='ignore')
				
				except MemoryError as me:
					log = 'Read log causes MemoryError: %s' % (me)
				
			print('semantic test compilation failed with ret %s: %s' % (ret, log))
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.SemaErrVR.build('Test Compilation Failed', 'Test compilation failed\n%s\n%s\n' % (log, self.status["vali_detail"]))
			return False
		
		# run the modified fuzz driver
		def do_test(testcase):
			oldpwd = os.getcwd()
			os.chdir(self.cfg.basedir)

			print('run semantic test with testcase %s' % (repr(testcase)))
			with open(self.cfg.testcase, 'w') as f:
				f.write(testcase)
			runcmd = '%s %s 1> %s 2>&1' % (self.cfg.testexe, self.cfg.testcase, self.cfg.testlog)
			print('semantic test command: %s' % (runcmd))
			ret = os.system(runcmd)

			os.chdir(oldpwd)

			log = None
			with open(self.cfg.testlog, 'rb') as f:
				try:
					raw_log = f.read(-1)
					log = raw_log.decode('utf-8', errors='ignore')
				
				except MemoryError as me:
					log = 'Read log causes MemoryError: %s' % (me)

			# analyze result
			if ret != 0:
				return 'SEMA-TEST-ERROR: ret %s for testcase %s\n%s\n' % (ret, testcase, log)

			else:
				return log
		
		passed, test_err = checker.do_check(do_test)
		print('passed is %s, test_err is %s' % (passed, test_err))
		if 'SEMA-TEST-ERROR' in test_err:
			# error
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.SemaErrVR.build('Test Failed', 'Test failed\n%s\n%s\n' % (test_err, self.status["vali_detail"]))
			return False
		
		if not passed:
			# error
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.SemaErrVR.build('Test Not Pass', 'Test not pass\n%s\n%s\n' % (test_err, self.status["vali_detail"]))
			return False

		print('semantic test for %s passed' % (sig))
		return True

	def check_by_code_checker(self, checker):
		code = self.show_code()

		passed, check_err = checker.do_check(code)
		print('code checker passed is %s, check_err is %s' % (passed, check_err))
		if check_err.startswith('CODE-CHECK-ERROR'):
			# error
			print('come here 1')
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.SemaErrVR.build('Code Check Failed', 'Code check failed\n%s\n%s\n' % (check_err, self.status["vali_detail"]))
			return False
		
		if not passed:
			# error
			print('come here 2')
			self.status['error_detected'] = True
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.SemaErrVR.build('Code Check Not Pass', 'Code check not pass\n%s\n%s\n' % (check_err, self.status["vali_detail"]))
			return False

		print('code checker for %s passed' % (sig))
		return True

	def check_by_always_false_checker(self, checker):
		# error
		self.status['error_detected'] = True
		self.status['vali_phase'] = 'semantic'
		self.status['vali_result'], self.status["vali_detail"] = libVR.SemaErrVR.build('Always False Check Not Pass', 'Always false check not pass\n%s\n%s\n' % ('always false due to the miss of server logic', self.status["vali_detail"]))
		return False

	def check_semantic(self, sema):
		global sig 

		# currently we check the semantics of the data usage only 
		# we generate a modified fuzz driver based on libclang, and run it to check the semantics

		if sema:
			checkers = libSemanticChecker.get_fp_checkers(sig)
			print('checkers of %s are: %s' % (sig, checkers))
			if len(checkers) != None:
				# TODO: currently we do not record all checker's check result but only the first failed one or the last succ one, we may need to improve it later
				for checker in checkers:
					if checker.ty == libSemanticChecker.SemanticTester.ty:
						if not self.check_by_semantic_tester(checker):
							# failed case has already been handled, just return
							return
					elif checker.ty == libSemanticChecker.CodeChecker.ty:
						if not self.check_by_code_checker(checker):
							# failed case has already been handled, just return
							return
					elif checker.ty == libSemanticChecker.AlwaysInvalidChecker.ty:
						if not self.check_by_code_checker(checker):
							# failed case has already been handled, just return
							return
					else:
						raise Exception('unknown semantic checker type %s' % (checker.ty))

			else:
				print('no semantic checker for %s' % (sig))

			self.status['error_detected'] = False
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.ValidVR.build('Semantic check has passed\n%s\n' % (self.status["vali_detail"]))
			return
		else:
			self.status['error_detected'] = False
			self.status['vali_phase'] = 'semantic'
			self.status['vali_result'], self.status["vali_detail"] = libVR.ValidVR.build('Semantic check has been disabled\n%s\n' % (self.status["vali_detail"]))
			return

	def get_fn_conds(self):
		global sig
		proj, api = self.cfg.target, sig

		fn_conds = []

		with open('/root/workspace/fuzzdrivergpt/meta/benchapidata.json', 'r') as f:
			benchapidata = json.load(f)
			for _, info in benchapidata.items():
				if info['proj'] == proj and info['api'] == api:
					fn_conds = info['fn_conds']

		return fn_conds

	def analyze_fuzz_result(self, check_fuzz_fns):
		# analyze result
		ret = self.process.poll()

		if check_fuzz_fns:
			vali_result, vali_detail = libVR.FuzzErrVR.analyze_fuzz_result(ret, self.cfg.fuzzlog, self.get_fn_conds())
			self.status['error_detected'] = (vali_result['ty'] != 'PTCK')
			self.status['vali_phase'] = 'fuzz'
			self.status['vali_result'], self.status["vali_detail"] = vali_result, 'FN check enabled.\n%s\n' % (vali_detail)

		else:
			vali_result, vali_detail = libVR.FuzzErrVR.analyze_fuzz_result(ret, self.cfg.fuzzlog, [])
			self.status['error_detected'] = (vali_result['ty'] != 'PTCK')
			self.status['vali_phase'] = 'fuzz'
			self.status['vali_result'], self.status["vali_detail"] = vali_result, 'FN check disabled.\n%s\n' % (vali_detail)

	def check_fuzz(self, check_fuzz_fns):
		# clean fuzz env (what left in previous fuzz env)
		if os.path.exists(self.cfg.artifactdir):
			shutil.rmtree(self.cfg.artifactdir, ignore_errors=True)
		os.makedirs(self.cfg.artifactdir)

		if os.path.exists(self.cfg.seeddir):
			shutil.rmtree(self.cfg.seeddir, ignore_errors=True)
		os.makedirs(self.cfg.seeddir)

		with open(self.cfg.fuzzsh, 'w') as f :
			f.write(self.cfg.runcmd)

		# fuzz certain seconds
		with open(self.cfg.fuzzlog, 'w') as f:

			self.process = subprocess.Popen(self.cfg.runcmd_subprocess, stdout=f, stderr=f)

			try:
				self.process.wait(timeout=90)

			except subprocess.TimeoutExpired as ex:
				# sometimes the fuzzer will stuck, we kill it after passing a safe & long time period
				self.process.kill()

		return self.analyze_fuzz_result(check_fuzz_fns)

	def validate_impl(self, query, fuzz=True, check_fuzz_fns=False, sema=False):
		self.reset()

		# 1. preprocess the generated code
		print('[1] text_truncation')
		self.text_truncation(query)
		self.sync_statusfile()
		if self.status['error_detected'] == True:
			print('[1] not passed text_truncation')
			return

		# 2. check compile error
		print('[2] check compilation')
		self.check_compile()
		self.sync_statusfile()
		if self.status['error_detected'] == True:
			print('[2] not passed compilation')
			return

		# 3. check link error
		print('[3] check build')
		self.check_link()
		self.sync_statusfile()
		if self.status['error_detected'] == True:
			print('[3] not passed build')
			return

		if fuzz:
			# 4. check fuzz
			print('[4] check fuzz')
			self.check_fuzz(check_fuzz_fns)
			self.sync_statusfile()
			if self.status['error_detected'] == True:
				print('[4] not passed fuzz check')
				return

			# 5. customized semantic checker
			print('[5] check semantic')
			self.check_semantic(sema)
			self.sync_statusfile()
			if self.status['error_detected'] == True:
				print('[5] not passed semantic check')
				return

	def concat_queried_code(self, query, solution, included=None):
		#solution = solution.replace('\n=======\n\n', '')
		solution = solution.replace('=======', '').strip('\n')
		#solution = solution.strip()

		general_code = ''
		if self.cfg.language == 'c':
			general_code = '#include <stdio.h>\n#include <unistd.h>\n#include <string.h>\n#include <stdlib.h>\n#include <stdint.h>\n#include <stdbool.h>\n#include <errno.h>\n'
		elif self.cfg.language == 'cpp':
			general_code = '#include <stdio.h>\n#include <unistd.h>\n#include <string.h>\n#include <stdlib.h>\n#include <stdint.h>\n#include <string>\n#include <fstream>\nusing namespace std;\n'

		target_code = self.cfg.precode
		if included:
			target_code = target_code + '\n' + included + '\n'

		#print('before query: \n%s\n --- \n' % (query))
		#print('before solution: \n%s\n --- \n' % (solution))

		if self.cfg.language == 'c':
			# replace the function signature as comment to avoid potential parsing error
			if 'Based on the above information, fix the code' in query:
				# if query is from IMPROVE, we just comment them all query and fix the solution
				query = '\n'.join( [ '// ' + line for line in query.strip().split('\n') ] )

				lines = []
				for line in solution.split('\n'):
					new_line = line
					if 'LLVMFuzzerTestOneInput' not in line:
						if line.startswith('extern'):
							new_line = "extern " + line
						elif (not self.cfg.autoinclude) and line.startswith('#include'):
							new_line = "// " + line
					else:
						if line.startswith('extern "C"'):
							new_line = line.replace('extern "C"', 'extern')
					lines.append(new_line)
				solution = '\n'.join(lines)

			else:
				lines = []
				for line in query.strip().split('\n'):
					new_line = line

					if 'LLVMFuzzerTestOneInput' not in line:
						if line.startswith('The following is a fuzz driver written'):
							new_line = '// ' + line
						elif line.startswith('extern'):
							new_line = re.sub(r'(extern.*(.*)\);)$', r'//\1', line, 1)
						elif (not self.cfg.autoinclude) and line.startswith('#include'):
							new_line = re.sub(r'(#include ".*")$', r'//\1', line, 1)

					lines.append(new_line)
				query = '\n'.join(lines)

		#print('after query: \n%s\n --- \n' % (query))
		#print('after solution: \n%s\n --- \n' % (solution))

		query_result = '\n'.join([ general_code, target_code, query, solution ])

		#print('query result: \n%s\n --- \n' % (query_result))

		return query_result
	
	#
	# The following three functions are outside control functions can be implemented in subclasses
	#

	def validate_wrap(self, query_result, fuzz, sync):
		raise Exception('Unimplemented Function validate_wrap in BaseValidator')

	def reset_fuzz(self):
		raise Exception('Unimplemented Function reset_fuzz in BaseValidator')

	def get_vali_status(self):
		raise Exception('Unimplemented Function get_vali_status in BaseValidator')

sig = None

def main():
	global sig

	pickleCfg, sig, fuzz, check_fuzz_fns, sema = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
	fuzz = True if fuzz == 'True' else False
	sema = True if sema == 'True' else False
	check_fuzz_fns = True if check_fuzz_fns == 'True' else False

	cfg = TargetCfg.pickleFrom(pickleCfg)
	query = None
	with open(cfg.outfile, 'r') as f:
		query = f.read(-1)
	validator = BaseValidator(cfg)

	validator.validate_impl(query, fuzz=fuzz, check_fuzz_fns=check_fuzz_fns, sema=sema)

if __name__ == '__main__':
	main()
