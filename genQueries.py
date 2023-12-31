import copy
import json
import argparse

from libTarget import TargetCfg

from apiusage.libContainerWrapper import ContainerAnalyzer
from apiusage import libAPIUsage
from generation import libPrompt

from ipdb import launch_ipdb_on_exception

import cfgs

import logging
logger = logging.getLogger(__name__)

debug = False

def main():
	global debug

	# parse args
	parser = argparse.ArgumentParser(description='hahaha')
	parser.set_defaults(workflow=None)

	subparsers = parser.add_subparsers(help='sub-command help')

	parser_gen = subparsers.add_parser('gen', help='generate prompt for a given api')
	parser_gen.add_argument('-l', '--language', required=True, help='languages e.g., c/c++/...')
	parser_gen.add_argument('-D', '--debug', required=False, action='store_true', help='debug mode')
	parser_gen.add_argument('--chatgpt', required=False, action='store_true', help='query is for chatgpt or not')
	parser_gen.add_argument('-o', '--output', required=False, default='./input_queries.json', help='the file generated query json written to')
	parser_gen.add_argument('-q', '--querymode', required=True, choices=['NAIVE', 'SMKTST', 'BACTX', 'DOCTX', 'UGCTX', 'SGUGCTX', 'ALLUGCTX'], help='query generation modes')
	parser_gen.add_argument('-t', '--target', required=True, help='target project')
	parser_gen.add_argument('-f', '--funcsig', required=True, help='target API function signature')
	parser_gen.set_defaults(workflow='gen')

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

	args = parser.parse_args()

	if not cfgs.check_and_load_cfgs(check_openai_keys=False):
		logger.error('cfgs check failed, exit')
		exit(1)

	workflow = args.workflow
	if workflow is None:
		logger.error('please specify workflow')
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

		analyzer = ContainerAnalyzer(TargetCfg(basedir=cfgs.FDGPT_WORKDIR,build_cfgs_yml=buildyml, target=target))
		analyzer.analyze_wrap('IMPROVE', {'query': query, 'solutionIdx': solutionidx, 'aaInfo': aainfo})
		with open(analyzer.cfg.queryfile, 'r') as f:
			queries = json.load(f)
			for idx in range(len(queries)):
				logger.info('-' * 12 + ' Query %s ' % (idx + 1) + '-' * 12)
				logger.info(queries[idx])
				logger.info('\n')

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

			analyzer = ContainerAnalyzer(TargetCfg(basedir=cfgs.FDGPT_WORKDIR, build_cfgs_yml=buildyml, target=target))
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

	elif workflow == 'gen':
		# prepare arg-related vars
		language = args.language.lower()
		target = args.target
		debug = args.debug
		funcsig = args.funcsig
		outfile = args.output
		querymode = args.querymode
		to_chatgpt = args.chatgpt
		buildyml = 'yml/' + language + '.yml'

		print('-' * 30)
		print('Language: %s' % (language))
		print('Target: %s' % (target))
		print('FuncSig: %s' % (funcsig))
		print('Debug: %s' % (debug))
		print('Output: %s' % (outfile))
		print('QueryMode: %s' % (querymode))
		print('ToChatGPT: %s' % (to_chatgpt))
		print('BuildYml: %s' % (buildyml))
		print('-' * 30)

		# main logic
		queries = []

		logger.info('=== handling %s ===' % (target))

		targetcfg = TargetCfg(basedir=cfgs.FDGPT_WORKDIR, build_cfgs_yml=buildyml, target=target)
		apiusages = libAPIUsage.APIUsage.buildAPIUsages(targetcfg)

		queries = libPrompt.genQueries(querymode, targetcfg, {'to_chatgpt': to_chatgpt, 'targetapis': [ funcsig ], 'apiusages': apiusages, 'debug': debug})

		# dump queries to json
		with open(outfile, 'w') as f:
			json.dump(queries, f, indent=2)

if __name__ == '__main__':
	with launch_ipdb_on_exception():
		main()
