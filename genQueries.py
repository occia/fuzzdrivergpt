import os
import copy
import json
import time
import utils
import docker
import pickle
import argparse
import threading
import traceback

from libTarget import TargetCfg
from libHeaderAnalyzer import BaseAnalyzer

from ipdb import launch_ipdb_on_exception

import cfgs

debug = False

class ContainerAnalyzer(BaseAnalyzer):

	def __init__(self, cfg):
		super().__init__(cfg)
		if not os.path.exists(self.cfg.workdir):
			os.makedirs(self.cfg.workdir, exist_ok=True)
		self.docker = None

	def analyze_wrap(self, querymode, params):
		global debug

		if self.cfg.language == 'c':
			TargetCfg.pickleTo(self.cfg, self.cfg.headerpickle)
			with open(self.cfg.headerparampickle, 'wb') as f:
				pickle.dump(params, f)

			dockercmd = 'python3 /root/workspace/fuzzdrivergpt/libHeaderAnalyzer.py %s %s %s' % (self.cfg.headerpickle, querymode, self.cfg.headerparampickle)
			if debug:
				print(dockercmd)
				dockercmd = 'sleep 10h'
			imagename = self.cfg.imagename
			dockervolumns = [
				#'%s/targets/%s:/root/workspace/fuzzdrivergpt/install' % (cfgs.get_proj_dir(), self.cfg.target),
				'%s:%s' % (self.cfg.workdir, self.cfg.workdir),
				'%s:%s' % (self.cfg.cachedir, self.cfg.cachedir),
				'%s/libTarget.py:/root/workspace/fuzzdrivergpt/libTarget.py' % (cfgs.get_proj_dir()),
				'%s/libHeaderAnalyzer.py:/root/workspace/fuzzdrivergpt/libHeaderAnalyzer.py' % (cfgs.get_proj_dir()),
				'%s/libManualAPIDoc.py:/root/workspace/fuzzdrivergpt/libManualAPIDoc.py' % (cfgs.get_proj_dir()),
				'%s/meta/benchmarkapis.json:/tmp/benchmarkapis.json' % (cfgs.get_proj_dir()),
				'%s/libImproveQueryGen.py:/root/workspace/fuzzdrivergpt/libImproveQueryGen.py' % (cfgs.get_proj_dir()),
				'%s/libVR.py:/root/workspace/fuzzdrivergpt/libVR.py' % (cfgs.get_proj_dir()),
			]

			if querymode == 'UGCTX' or querymode == 'SGUGCTX' or querymode == 'ALLUGCTX' or querymode == 'IMPROVE' or querymode == 'ANALYZE':
				if os.path.exists(cfgs.FDGPT_JDK):
					dockervolumns.append("%s:/root/workspace/fuzzdrivergpt/jdk-19.0.2" % (cfgs.FDGPT_JDK))

				dockervolumns.append("%s:/tmp/cc-func-parser-0.5-jar-with-dependencies.jar" % (cfgs.FDGPT_ANTLR))

				if querymode == 'SGUGCTX' or querymode == 'ALLUGCTX' or querymode == 'IMPROVE':
					dockervolumns.append("%s:/tmp/crawled_usage.json" % (cfgs.FDGPT_CRAWLED_USAGE))
				
				if querymode == 'ANALYZE':
					driverfile = params['targetDriverFile']
					outfile = params['outJsonFile']
					with open(outfile, 'w') as f:
						f.write('aaa')

					driverfile = os.path.abspath(driverfile)
					outfile = os.path.abspath(outfile)

					dockervolumns.append('%s:/tmp/analyze_target_driver.c' % (driverfile))
					dockervolumns.append('%s:/tmp/analyze_result.json' % (outfile))

			workdir = self.cfg.workdir

			# run the docker
			client = docker.from_env()

			try:
				self.docker = client.containers.run(imagename, command=dockercmd, volumes=dockervolumns, working_dir=workdir, privileged=True, remove=False, detach=True)

			except Exception as ex:
				print('meet exception when run docker %s' % (ex))
				raise ex

			if debug:
				print('docker exec -it %s bash' % (self.docker.name))
				os._exit(0)

			self.docker.reload()
			rets = self.docker.wait()
			if rets['StatusCode'] != 0:
				print('container does not start as expected, check the logs:\n%s' % (self.docker.logs()))
				raise Exception('starting container meets error')
			
			self.docker.remove(force=True)

			print('[+] query file %s has been created' % (self.cfg.queryfile))
		else:
			raise Exception('Unsupported language %s' % (self.cfg.language))

def main():
	global debug

	# parse args
	parser = argparse.ArgumentParser(description='hahaha')
	parser.set_defaults(workflow=None)

	subparsers = parser.add_subparsers(help='sub-command help')

	parser_batch = subparsers.add_parser('batch', help='batch generation mode')
	parser_batch.add_argument('-l', '--language', required=True, help='languages e.g., c/c++/...')
	parser_batch.add_argument('-D', '--debug', required=False, action='store_true', help='debug mode')
	parser_batch.add_argument('--chatgpt', required=False, action='store_true', help='query is for chatgpt or not')
	parser_batch.add_argument('--cotlevel', required=False, type=int, default=0, help='use cot1 in query')
	#parser_batch.add_argument('-o', '--output', required=False, default='./input_queries.json', help='the file generated query json written to')
	parser_batch.add_argument('-q', '--querymode', required=True, choices=['NAIVE', 'SMKTST', 'BACTX', 'DOCTX', 'UGCTX', 'SGUGCTX', 'ALLUGCTX'], help='query generation modes')
	parser_batch.add_argument('target', nargs='+', help='target project names e.g., jsonnet/libaom/...')
	parser_batch.set_defaults(workflow='batch')

	parser_improve = subparsers.add_parser('improve', help='generate improve query')
	parser_improve.add_argument('-D', '--debug', required=False, action='store_true', help='debug mode')
	parser_improve.add_argument('-v', '--validatedfile', required=True, help='validated json file')
	parser_improve.add_argument('-q', '--queryid', required=True, help='target queryid')
	parser_improve.add_argument('-aa', '--additionalinfo', required=False, action='store_true', help='whether to add additional related info in improved query')
	parser_improve.add_argument('-i', '--solutionidx', required=True, type=int, help='target solution index')
	parser_improve.set_defaults(workflow='improve')

	parser_listimprove = subparsers.add_parser('listimprove', help='generate improve queries')
	parser_listimprove.add_argument('-v', '--validatedfile', required=True, help='validated json file')
	parser_listimprove.add_argument('-aa', '--additionalinfo', required=False, action='store_true', help='whether to add additional related info in improved query')
	parser_listimprove.add_argument('-o', '--outfile', required=True, help='output json file')
	parser_listimprove.set_defaults(workflow='listimprove')

	parser_analyze = subparsers.add_parser('analyze', help='analyze the driver')
	parser_analyze.add_argument('-l', '--language', required=True, help='languages e.g., c/c++/...')
	parser_analyze.add_argument('-t', '--target', required=True, help='target project names e.g., jsonnet/libaom/...')
	parser_analyze.add_argument('-i', '--targetdriverfile', required=True, help='target driver file')
	parser_analyze.add_argument('-o', '--outjsonfile', required=True, help='analyze result json file')
	parser_analyze.set_defaults(workflow='analyze')

	args = parser.parse_args()

	workflow = args.workflow
	if workflow is None:
		print('please specify workflow')
		parser.print_help()
		exit(1)

	elif workflow == 'improve':
		debug = args.debug
		validatedfile = args.validatedfile
		queryid = args.queryid
		solutionidx = args.solutionidx
		aainfo = args.additionalinfo

		query = None
		with open(validatedfile, 'r') as f:
			validated = json.load(f)
			query = validated[queryid]

		language = query['language']
		target = query['target']
		buildyml = 'yml/' + language + '.yml'

		print('-' * 30)
		print('Language: %s' % (language))
		print('Target: %s' % (target))
		print('Debug: %s' % (debug))
		print('ValidatedFile: %s' % (validatedfile))
		print('QueryID: %s' % (queryid))
		print('SolutionIdx: %s' % (solutionidx))
		print('AdditionalInfo: %s' % (aainfo))
		print('BuildYml: %s' % (buildyml))
		print('-' * 30)

		analyzer = ContainerAnalyzer(TargetCfg(build_cfgs_yml=buildyml, target=target))
		analyzer.analyze_wrap('IMPROVE', {'query': query, 'solutionIdx': solutionidx, 'aaInfo': aainfo})
		with open(analyzer.cfg.queryfile, 'r') as f:
			queries = json.load(f)
			for idx in range(len(queries)):
				print('-' * 12 + ' Query %s ' % (idx + 1) + '-' * 12)
				print(queries[idx])
				print('\n')

	elif workflow == 'listimprove':
		validatedfile = args.validatedfile
		aainfo = args.additionalinfo
		out = args.outfile

		invalid = []
		with open(validatedfile, 'r') as f:
			validated = json.load(f)
			for query in validated.values():
				if query['result']['validations'][0]['vali_result']['ty'] != 'VAL':
					invalid.append(query)
		
		improve_list = []
		for query in invalid:
			language = query['language']
			target = query['target']
			buildyml = 'yml/' + language + '.yml'
			queryid = query['id']
			solutionidx = 0

			analyzer = ContainerAnalyzer(TargetCfg(build_cfgs_yml=buildyml, target=target))
			analyzer.analyze_wrap('IMPROVE', {'query': query, 'solutionIdx': solutionidx, 'aaInfo': aainfo})

			with open(analyzer.cfg.queryfile, 'r') as f:
				query_ctnts = json.load(f)
				for query_ctnt in query_ctnts:
					new_query = copy.deepcopy(query)
					new_query['query'] = query_ctnt
					if aainfo:
						new_query['id'] = queryid + '-AAINFO-IMPROVE'
					else:
						new_query['id'] = queryid + '-IMPROVE'
					new_query['queryMode'] = new_query['queryMode'] + '-IMPROVE'
					if 'improveHistory' not in new_query:
						new_query['improveHistory'] = [ queryid ]
					else:
						new_query['improveHistory'].append(queryid)
					del new_query['result']

					improve_list.append(new_query)
		
		with open(out, 'w') as f:
			json.dump(improve_list, f, indent=2, sort_keys=True)

	elif workflow == 'batch':
		# prepare arg-related vars
		language = args.language.lower()
		targets = args.target
		debug = args.debug
		#outfile = args.output
		querymode = args.querymode
		to_chatgpt = args.chatgpt
		cot_level = args.cotlevel
		buildyml = 'yml/' + language + '.yml'

		print('-' * 30)
		print('Language: %s' % (language))
		print('Targets: %s' % (targets))
		print('Debug: %s' % (debug))
		#print('Output: %s' % (outfile))
		print('QueryMode: %s' % (querymode))
		print('ToChatGPT: %s' % (to_chatgpt))
		print('CotLevel: %s' % (cot_level))
		print('BuildYml: %s' % (buildyml))
		print('-' * 30)

		# main logic
		queries = []

		for target in targets:
			print('=== handling %s ===' % (target))

			analyzer = ContainerAnalyzer(TargetCfg(build_cfgs_yml=buildyml, target=target))
			analyzer.analyze_wrap(querymode, {'toChatGpt': to_chatgpt, 'cotLevel': cot_level})

		## dump queries to json
		#with open(outfile, 'w') as f:
		#	json.dump(queries, f, indent=2)

	elif workflow == 'analyze':
		targetdriverfile = args.targetdriverfile
		language = args.language.lower()

		target = args.target
		outjsonfile = args.outjsonfile

		buildyml = 'yml/' + language + '.yml'

		print('-' * 30)
		print('Language: %s' % (language))
		print('Target: %s' % (target))
		print('TargetDriverFile: %s' % (targetdriverfile))
		print('OutJsonFile: %s' % (outjsonfile))
		print('-' * 30)

		analyzer = ContainerAnalyzer(TargetCfg(build_cfgs_yml=buildyml, target=target))
		analyzer.analyze_wrap('ANALYZE', {'targetDriverFile': targetdriverfile, 'outJsonFile': outjsonfile})

if __name__ == '__main__':
	with launch_ipdb_on_exception():
		main()
