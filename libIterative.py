import re
import os
import sys
import copy
import json
import time
import uuid
import pickle
import random
import requests

import argparse

import cfgs
import libVR
import libQuery
import libTarget
import genQueries
import handleChatGPTResult

import logging
logger = logging.getLogger(__name__)

class IterativeQueryRecord:
	def __init__(self, model, language, target, funcsig, improvestrategy, validatorUrl, headersAuth, initialQueryMode, recordIdx):
		self.model = model
		self.language = language
		self.target = target
		self.funcsig = funcsig

		self.buildyml = 'yml/' + language + '.yml'

		self.initialQueryMode = initialQueryMode

		self.improvestrategy = improvestrategy
		self.curQueryIDs = []
		self.queries = {}

		self.id = str(uuid.uuid4())
		self.qid_bases = set([])
		self.remotePathPrefix = '/root/workspace/remote-sshfs'
		self.localInPath = '%s/tasks/queries-%s.json' % (cfgs.FDGPT_WORKDIR, self.id)
		self.localOutPath = '%s/tasks/validations-%s.json' % (cfgs.FDGPT_WORKDIR, self.id)
		self.remoteInPath = '%s/%s' % (self.remotePathPrefix, self.localInPath)
		self.remoteOutPath = '%s/%s' % (self.remotePathPrefix, self.localOutPath)

		self.headersAuth = headersAuth
		self.validatorUrl = validatorUrl

		if self.validatorUrl == None:
			raise Exception('invalid validatorUrl: %s' % (self.validatorUrl))

		self.url_vali = '%s/validate' % (self.validatorUrl)
		self.url_status = '%s/status' % (self.validatorUrl)

		self._recordIdx = recordIdx
		self.recordIdx = 'iter-account-%s-' % (self._recordIdx)

		# acceptQueryIDs: queries that have acceptable validation results, it is a subset of leafQueryIDs
		self.acceptQueryIDs = set([])
		# leafQueryIDs: queries that do not need to be improved any more (has acceptable result or cannot be improved, etc)
		self.leafQueryIDs = set([])

		os.makedirs('%s/tasks' % (cfgs.FDGPT_WORKDIR), exist_ok=True)

	def cleanTmp(self):
		if os.path.exists(self.localInPath):
			os.remove(self.localInPath)
		if os.path.exists(self.localOutPath):
			os.remove(self.localOutPath)

	def printQuery(self, qid):
		query = self.queries[qid]
		if 'validations' not in query['result']:
			logger.info('%s -> %s' % (qid, query['result']['status'])) 
		else:
			vr = libVR.BasicVR.load(query['result']['validations'][0]['vali_result'])
			logger.info('%s -> %s' % (qid, vr.taxon)) 

	def printIterationProcess(self, qid):
		query = self.queries[qid]
		if 'improveHistory' in query:
			for _qid in query['improveHistory']:
				self.printQuery(_qid)
		
		self.printQuery(qid)
	
	def dumpQueriesJson(self):
		return json.dumps(self.queries, indent=2, sort_keys=True)

	def getQidBase(self, qid):
		matched_base, matched_len = None, 0
		for qid_base in self.qid_bases:
			if qid.startswith(qid_base):
				if matched_len < len(qid_base):
					matched_base, matched_len = qid_base, len(qid_base)
		return matched_base

	def generateAAQueries(self, last_query):
		next_queries = []

		cfg = libTarget.TargetCfg(basedir=cfgs.FDGPT_WORKDIR, build_cfgs_yml=self.buildyml, target=self.target, task_idx=self.recordIdx)
		analyzer = genQueries.ContainerAnalyzer(cfg)
		analyzer.analyze_wrap('IMPROVE', {'query': last_query, 'solutionIdx': 0, 'aaInfo': True, 'funcsig' : self.funcsig})

		with open(analyzer.cfg.queryfile, 'r') as f:
			next_query_ctnts = json.load(f)
			for query_ctnt in next_query_ctnts:
				next_query = copy.deepcopy(last_query)

				next_query['query'] = query_ctnt
				next_query['id'] = self.getQidBase(last_query['id']) + '-AAIMPROVE'
				next_query['improveHistory'].append(last_query['id'])

				del next_query['result']
				next_queries.append(next_query)

		return next_queries

	def generateBAQueries(self, last_query):
		next_queries = []

		cfg = libTarget.TargetCfg(basedir=cfgs.FDGPT_WORKDIR, build_cfgs_yml=self.buildyml, target=self.target, task_idx=self.recordIdx)
		analyzer = genQueries.ContainerAnalyzer(cfg)
		analyzer.analyze_wrap('IMPROVE', {'query': last_query, 'solutionIdx': 0, 'aaInfo': False, 'funcsig': self.funcsig})

		with open(analyzer.cfg.queryfile, 'r') as f:
			next_query_ctnts = json.load(f)
			for query_ctnt in next_query_ctnts:
				next_query = copy.deepcopy(last_query)

				next_query['query'] = query_ctnt
				next_query['improveHistory'].append(last_query['id'])
				next_query['id'] = self.getQidBase(last_query['id']) + '-BAIMPROVE'

				del next_query['result']
				next_queries.append(next_query)
		
		return next_queries

	def addNewQueryAsNext(self, new_query):
		new_query['id'] = new_query['id'] + '-' + str(len(self.queries))
		self.queries[new_query['id']] = new_query

	def generateInitialQueries(self, initialMode):
		queries = []

		cfg = libTarget.TargetCfg(basedir=cfgs.FDGPT_WORKDIR, build_cfgs_yml=self.buildyml, target=self.target, task_idx=self.recordIdx)
		analyzer = genQueries.ContainerAnalyzer(cfg)
		analyzer.analyze_wrap(initialMode, {'toChatGpt': True, 'funcsig': self.funcsig})
		with open(analyzer.cfg.queryfile, 'r') as f:
			gen_queries = json.load(f)
			for query in gen_queries:
				if query['info']['mangled_name'] == self.funcsig:
					queries.append(query)

		return queries

	def generateNextQueries(self):
		# generate next queries
		next_queries = []
		if ('gpt-3.5' in self.model) or ('gpt-4' in self.model):
			if len(self.queries) == 0:
				# initial query
				gen_queries, new_queries = [], []
				if self.initialQueryMode == 'ALLCTX':
					gen_queries.extend( self.generateInitialQueries('BACTX') )
					gen_queries.extend( self.generateInitialQueries('ALLUGCTX') )
				else:
					gen_queries.extend( self.generateInitialQueries(self.initialQueryMode) )

				for query in gen_queries:
					if libQuery.token_length_exceeded(self.model, query['query']) <= 0:
						new_queries.append(query)

				if len(new_queries) != 0:
					first_query = random.choice(new_queries)

					qid_base = first_query['id']
					first_query['id'] = qid_base + '-INITIAL'
					first_query['improveHistory'] = []

					self.qid_bases.add(qid_base)
					self.addNewQueryAsNext(first_query)
					next_queries.append(first_query)

			else:
				# query based on previous validation result
				for last_query_id in self.curQueryIDs:
					last_query = self.queries[last_query_id]

					gen_queries, new_queries = [], []

					if self.improvestrategy == 'AA':
						gen_queries = self.generateAAQueries(last_query)

					elif self.improvestrategy == 'BA':
						gen_queries = self.generateBAQueries(last_query)

					elif self.improvestrategy == 'ABA':
						gen_queries = self.generateAAQueries(last_query)
						gen_queries.extend( self.generateBAQueries(last_query) )

					else:
						raise Exception('Not implemented yet')

					# now randomly select one
					for query in gen_queries:
						if libQuery.token_length_exceeded(self.model, query['query']) <= 0:
							new_queries.append(query)

					if len(new_queries) != 0:
						next_query = random.choice(new_queries)
						self.addNewQueryAsNext(next_query)
						next_queries.append(next_query)
					else:
						# cannot improve, mark it as leaf
						self.leafQueryIDs.add(last_query_id)

		else:
			raise Exception('Not implemented yet')
		
		# load the generated queries
		self.curQueryIDs = []
		for query in next_queries:
			self.curQueryIDs.append(query['id'])

	def doRemoteQuery(self, query_ids=None):
		if ('gpt-3.5' in self.model) or ('gpt-4' in self.model):
			if query_ids == None:
				query_ids = self.curQueryIDs

			failed_ids = []
			for query_id in query_ids:
				logger.debug('querying ' + query_id + '...')
				query = self.queries[query_id]
				query['query'] = libQuery.shrink_query_usage_if_can(self.model, query['query'])
				query['result'] = libQuery.resilient_wrapper_query(self.model, query['query'])
				if query['result']['status'] != 'FinishedNormally':
					failed_ids.append(query_id)
				handleChatGPTResult.handleSingleResult(query)

				if query['result']['status'] != 'ERRLONGQUERY':
					# query via APIKEY do not need extra wait time
					pass

					#wait_sec = 100000
					#if 'gpt-4' in self.model:
					#	wait_sec = 7 * 60 + random.randint(30, 60)
					#elif 'gpt-3.5' in self.model:
					#	wait_sec = 7 * 6 * 3 + random.randint(9, 18)
					## NO need in api query mode
					#time.sleep(wait_sec)
			
			# remove failed queries from curQueryIDs
			if query_ids == self.curQueryIDs:
				for failed_id in failed_ids:
					self.curQueryIDs.remove(failed_id)

		else:
			raise Exception('Not implemented yet')

	def _do_validation_locally(self, qids):
		with open(self.localInPath, 'w') as f:
			curQueries = [ self.queries[qid] for qid in qids ]
			f.write(json.dumps(curQueries, indent=2, sort_keys=True))
		
		# run validation
		while True:
			ret = os.system("python validateQueries.py -a '.*' -i '.*' -T %s -j 5 -dj 1 %s -o %s" % (self.recordIdx, self.localInPath, self.localOutPath))
			if ret == 0:
				break
			else:
				logger.warning('Failed to validate queries, retrying...')
		
		# load validation result
		with open(self.localOutPath, 'r') as f:
			validationResult = json.load(f)
			for result in validationResult.values():
				qid = result['id']
				self.queries[qid]['result'] = result['result']

	def _do_validation_remotely(self, qids):
		with open(self.localInPath, 'w') as f:
			curQueries = [ self.queries[qid] for qid in qids ]
			f.write(json.dumps(curQueries, indent=2, sort_keys=True))

		resp = requests.post(self.url_vali, json={'inputjson': self.remoteInPath, 'outputjson': self.remoteOutPath}, headers=self.headersAuth, verify=False)
		if resp.status_code != 200:
			raise Exception('Failed to require validation: %s' % (resp))

		taskid = resp.json()['taskid']
		
		# wait for completion
		while True:
			resp = requests.post(self.url_status, json={'taskid' : taskid}, headers=self.headersAuth, verify=False)
			if resp.status_code != 200:
				raise Exception('Failed to get validation task status: %s' % (resp))

			resp = resp.json()
			if resp['status'] == 'unknown':
				raise Exception('Unknown taskid: %s' % (taskid))

			if resp['status'] == 'done':
				break
			
			time.sleep(3)
		
		# load the validation result
		with open(self.localOutPath, 'r') as f:
			validationResult = json.load(f)
			for result in validationResult.values():
				qid = result['id']
				self.queries[qid]['result'] = result['result']

	def _add_manual_validation_criteria(self, qids):
		# this ensures all manually configured validation criteria are used during validation
		for qid in qids:
			query = self.queries[qid]
			if 'validations' in query['result']:
				del query['result']['validations']
			query['semantic_check'] = True
			query['check_fuzz_fns'] = True

	def _do_validation(self, qids):
		self._add_manual_validation_criteria(qids)
		self._do_validation_locally(qids)
		#self._do_validation_remotely(qids)

	def doValidation(self):
		self._do_validation(self.curQueryIDs)

	def doAdditionalCheckForLeaves(self):
		self.refreshResultsIDs()

		self._add_manual_validation_criteria(self.leafQueryIDs)

		if len(self.leafQueryIDs) != 0:
			self._do_validation(self.leafQueryIDs)

	def isAcceptableResult(self, qid):
		if self.queries[qid]['result']['status'] == 'FinishedNormally':
			vali_result = self.queries[qid]['result']['validations'][0]['vali_result']
			vr = libVR.BasicVR.load(vali_result)
			if vr.ty == 'VAL':
				return True
			#elif vr.ty == 'ERR-FUZZ':
			#	# we accept the crashes found after 100 rounds
			#	if vr._round != None and vr._round > 100:
			#		return True
		
		return False

	def getValidationBrief(self, qid):
		if self.queries[qid]['result']['status'] == 'FinishedNormally':
			vali_result = self.queries[qid]['result']['validations'][0]['vali_result']
			vr = libVR.BasicVR.load(vali_result)
			return vr.taxon
		else:
			return 'unknown validation result'

	def refreshResultsIDs(self):
		self.acceptQueryIDs = set([])
		self.leafQueryIDs = set([])

		indegrees = {}
		for qid in self.queries.keys():
			refs = self.queries[qid]['improveHistory']
			for ref in refs:
				if ref not in indegrees:
					indegrees[ref] = 0
				indegrees[ref] += 1

		for qid in self.queries.keys():
			if self.isAcceptableResult(qid):
				self.acceptQueryIDs.add(qid)
			if qid not in indegrees:
				# no incoming edges, it is a leaf
				self.leafQueryIDs.add(qid)

	def hasAcceptableResults(self):
		self.refreshResultsIDs()

		return len(self.acceptQueryIDs) > 0
	
	def getAcceptableResults(self):
		self.refreshResultsIDs()

		return self.acceptQueryIDs

def summary(patterns, files):
	# load IterativeQueryRecord from pickle
	model_bins = {}
	ptrn_bins = {}

	ptrn2files = {}
	for pattern in patterns:
		for file in files:
			if re.search(pattern, file) != None:
				if pattern not in ptrn2files:
					ptrn2files[pattern] = set([])
				ptrn2files[pattern].add(file)

	covered_qstns = set([])
	ptrn_bins = {}
	for ptrn, pfiles in ptrn2files.items():
		bins = {}

		for file in pfiles:
			with open(file, 'rb') as f:
				iqr = pickle.load(f)
				iqr.refreshResultsIDs()
				#logger.debug('iqr %s %s %s %s %s' % (iqr.model, iqr.target, iqr.funcsig, iqr.improvestrategy, iqr.hasAcceptableResults()))

				qstn = (iqr.target, iqr.funcsig)

				# update covered_qstns
				covered_qstns.add(qstn)

				# update bins
				if qstn not in bins:
					bins[qstn] = []
				sum = []
				for qid in iqr.acceptQueryIDs:
					sum.append( len(iqr.queries[qid]['improveHistory']) + 1 )
				bins[qstn].extend(sum)

				# update model_bins
				if iqr.model not in model_bins:
					model_bins[iqr.model] = {}
				if qstn not in model_bins[iqr.model]:
					model_bins[iqr.model][qstn] = []
				model_bins[iqr.model][qstn].extend(sum)
		
		ptrn_bins[ptrn] = bins

	# show ptrn_bins
	print('Pattern bins:')
	for ptrn, bins in ptrn_bins.items():
		accs, all = set([]), set([])
		for qstn, passes in bins.items():
			all.add(qstn)
			if len(passes) > 0:
				accs.add(qstn)
		
		print('For pattern `%s`, there are %s/%s results (%.2f)' % (ptrn, len(accs), len(all), len(accs) / (len(all) * 1.0)))

	# show model_bins
	print('\n')
	print('Model bins:')
	for model, bins in model_bins.items():
		accs, all = set([]), set([])
		for qstn, passes in bins.items():
			all.add(qstn)
			if len(passes) > 0:
				accs.add(qstn)
		
		print('For model `%s`, there are %s/%s results (%.2f)' % (model, len(accs), len(all), len(accs) / (len(all) * 1.0)))

	# show detailed results per qstn
	print('\n')
	print('Detailed results per qstn:')

	# get title row
	columns = ptrn2files.keys()
	title_row = [ '-' ]
	title_row.extend(columns)

	# get ctnt rows
	ctnt_rows = []
	covered_qstns = list(covered_qstns)
	covered_qstns.sort()
	for qstn in covered_qstns:
		row = [ '%s_%s' % (qstn) ]

		for column in columns:
			ptrn = column
			bins = ptrn_bins[ptrn]
			if qstn in bins:
				if len(bins[qstn]) == 0:
					row.append( '0' )
				else:
					row.append( ','.join([ str(i) for i in bins[qstn] ]) )
			else:
				row.append( '-' )

		ctnt_rows.append(row)
	
	out = ''

	column_length = []
	for idx in range(len(title_row)):
		max_length = len(title_row[idx])
		for row in ctnt_rows:
			if len(row[idx]) > max_length:
				max_length = len(row[idx])
		# adjust max_length to be smallest multiple of 4 which is larger than max_length
		max_length = (max_length // 4 + 1) * 4
		column_length.append(str(max_length))

	# print title row
	for idx in range(len(title_row)):
		column = title_row[idx]
		out += ('%-' + column_length[idx] + 's') % (column)
	out += '\n'

	# print ctnt rows
	for ctnt_row in ctnt_rows:
		for idx in range(len(ctnt_row)):
			column = ctnt_row[idx]
			out += ('%-' + column_length[idx] + 's') % (column)
		out += '\n'

	print(out)

def detailOneQuery(console, query, verbose):
	from rich.markdown import Markdown

	if verbose == 0:
		if 'validations' not in query['result']:
			console.print(Markdown('%s\t--\t%s\n' % (query['id'], query['result']['status'])))
		else:
			vr = libVR.BasicVR.load(query['result']['validations'][0]['vali_result'])
			console.print(Markdown('%s\t--\t%s\n' % (query['id'], vr.taxon)))
	else:
		console.print(Markdown('---'))
		console.print(Markdown('**Query: %s**\n' % query['id']))
		console.print(query['query'])
		console.print(Markdown('**Response:**\n'))
		console.print(query['result']['raw_solutions'][0])
		console.print(Markdown('**ValidationResult:**\n'))
		vr = libVR.BasicVR.load(query['result']['validations'][0]['vali_result'])
		console.print(vr.taxon)
		console.print('\n'.join(vr.detail.split('\n')[:30]))

def detail(file, verbose):
	from rich.console import Console
	from rich.markdown import Markdown

	console = Console()

	with open(file, 'rb') as f:
		iqr = pickle.load(f)
		iqr.refreshResultsIDs()

		for qid in iqr.leafQueryIDs:
			query = iqr.queries[qid]
			console.print(Markdown('---'))
			console.print(Markdown('## QID %s' % qid))
			if 'improveHistory' in query:
				for _qid in query['improveHistory']:
					# print the history
					_query = iqr.queries[_qid]
					detailOneQuery(console, _query, verbose)

			# lastly print itself
			detailOneQuery(console, query, verbose)

def addsemacheck(files):
	all, notadd = 0, 0
	for file in files:
		with open(file, 'rb') as f:
			iqr = pickle.load(f)
			iqr.refreshResultsIDs()

			for qid in iqr.acceptQueryIDs:
				if 'semantic_check' not in iqr.queries[qid]:
					notadd += 1
				all += 1

	print('Total %s queries, %s not added' % (all, notadd))

def trunclongquery(files):
	handled = 0

	for file in files:
		if not file.endswith('.pickle'):
			print('skip non pickle file %s' % file)
			continue

		iqr = None
		with open(file, 'rb') as f:
			iqr = pickle.load(f)

		requery_ids = []

		for qid in iqr.queries.keys():
			query = iqr.queries[qid]
			if query['result']['status'] == 'ERRLONGQUERY':
				requery_ids.append(qid)
				del query['result']
				query['query'] = libQuery.shrink_query_usage_if_can(iqr.model, query['query'])

		if len(requery_ids) == 0:
			continue

		print('Requerying %s queries in %s' % (len(requery_ids), file))
		iqr.doRemoteQuery(query_ids=requery_ids)
		handled += len(requery_ids)

		print('will write to %s' % file.replace('.pickle', '.json'))
		with open(file.replace('.pickle', '.json'), 'w') as f:
			f.write(iqr.dumpQueriesJson())
		with open(file, 'wb') as f:
			pickle.dump(iqr, f)
	
	print('Requery handled: %s' % (handled))

def main():
	parser = argparse.ArgumentParser(description='Iterative Query Record Related Utilities')
	parser.set_defaults(workflow=None)

	subparsers = parser.add_subparsers(help='sub-command help')

	parser_summ = subparsers.add_parser('summary', aliases=['sum'], help='summary help')
	parser_summ.add_argument('-f', '--files', metavar='file', type=str, nargs='+', required=True, help='files to be processed')
	parser_summ.add_argument('-p', '--patterns', type=str, nargs='+', required=True, help='patterns to be matched', default=[])
	parser_summ.set_defaults(workflow='summary')

	parser_detail = subparsers.add_parser('detail', aliases=['dtl'], help='detail help')
	parser_detail.add_argument('file', type=str, help='file to be processed')
	parser_detail.add_argument('-v', '--verbose', type=int, help='verbose level, from 0 to 3, higher number means more verbose output', default=0)
	parser_detail.set_defaults(workflow='detail')

	parser_addsemacheck = subparsers.add_parser('addsemacheck', aliases=['asc'], help='add semacheck help')
	parser_addsemacheck.add_argument('-f', '--files', metavar='file', type=str, nargs='+', required=True, help='files to be processed')
	parser_addsemacheck.set_defaults(workflow='addsemacheck')

	parser_trunclongquery = subparsers.add_parser('trunclongquery', aliases=['tlq'], help='truncate long query')
	parser_trunclongquery.add_argument('-f', '--files', metavar='file', type=str, nargs='+', required=True, help='files to be processed')
	parser_trunclongquery.set_defaults(workflow='trunclongquery')
	parser_trunclongquery.add_argument('-A', '--accountidx', required=True, type=int, help='account used for chatgpt')

	args = parser.parse_args()
	
	workflow = args.workflow
	if workflow == None:
		parser.print_help()
		exit(1)	

	elif workflow == 'summary':
		logger.info('Running summary...')

		patterns = args.patterns
		files = args.files

		print('-' * 30)
		print('patterns: %s' % (patterns))
		print('files: %s' % (files))
		print('-' * 30)

		summary(patterns, files)

	elif workflow == 'detail':
		logger.info('Running detail...')

		file = args.file
		verbose = args.verbose

		print('-' * 30)
		print('file: %s' % (file))
		print('verbose: %s' % (verbose))
		print('-' * 30)

		detail(file, verbose)
	
	elif workflow == 'addsemacheck':
		logger.info('Running addsemacheck...')

		files = args.files

		print('-' * 30)
		print('files: %s' % (files))
		print('-' * 30)

		addsemacheck(files)
	
	elif workflow == 'trunclongquery':
		logger.info('Truncating long query and requery...')

		files = args.files
		accountidx = args.accountidx

		print('-' * 30)
		print('files: %s' % (files))
		print('accountidx: %s' % (accountidx))
		print('-' * 30)

		libQuery.chatgpt_url = libQuery.chatgpt_plus_urls[accountidx % len(libQuery.chatgpt_plus_urls)]
		trunclongquery(files)

if __name__ == '__main__':
	main()
