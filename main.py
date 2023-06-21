import os
import pickle
import argparse

import libQuery
from libTarget import TargetCfg
from libIterative import IterativeQueryRecord

from prepareOSSFuzzImage import is_fuzzdrivergpt_image_exist, get_fuzzdrivergpt_imgname

import cfgs

def iterative_workflow(rounds, maxiterations, initialquerymode, accountidx, model, language, target, funcsig, improvestrategy, disablevalidation, outputjson):

	# not use currently
	headersAuth = { 'Authorization': 'Bearer xxxxxxxx', }
	validator_url = 'https://xxx.xxx.xxx.xxx:xxx'

	query_record = IterativeQueryRecord(model, language, target, funcsig, improvestrategy, validator_url, headersAuth, initialquerymode, accountidx)

	iterations = 0

	while True:
		iterations += 1

		# generate query
		print('--- ROUND [%s] Iteration [%s]: generate query' % (rounds, iterations))
		query_record.generateNextQueries()

		print('current generated queries are: %s' % (query_record.curQueryIDs))
		if len(query_record.curQueryIDs) == 0:
			print('--- No more queries to generate, stop ---')
			break

		# get response of query 
		print('--- ROUND [%s] Iteration [%s]: get response' % (rounds, iterations))
		query_record.doRemoteQuery()
		if len(query_record.curQueryIDs) == 0:
			print('--- No more queries to generate, stop ---')
			break

		if disablevalidation:
			print('--- Skip validation ---')
			break

		# validate the response
		print('--- ROUND [%s] Iteration [%s]: validate response' % (rounds, iterations))
		query_record.doRemoteValidation()

		if query_record.hasAcceptableResults():
			break

		if iterations >= maxiterations:
			break

	# find a valid response, record and end
	print('--- Round [%s] finished ---' % (rounds))
	print('All iteration results:')
	for qid in query_record.leafQueryIDs:
		print('qid: %s' % (qid))
		query_record.printIterationProcess(qid)

	# dump per round result
	round_outputjson = outputjson.replace('.json', '_round%s.json' % (rounds))
	with open(round_outputjson, 'w') as f:
		f.write(query_record.dumpQueriesJson())

	# comment for future use
	#round_outputpickle = outputjson.replace('.json', '_round%s.pickle' % (rounds))
	#with open(round_outputpickle.replace('.json', '.pickle'), 'wb') as f:
	#	pickle.dump(query_record, f)

	return query_record

def main_workflow(language, model, target, funcsig, querystrategy, disablevalidation, maxiterations, maxrounds, outputjson):
	rounds = 0

	if querystrategy == 'ITER-ALL':
		initialquerymode = 'ALLCTX'
		improvestrategy = 'ABA'
	elif querystrategy == 'ITER-BA':
		initialquerymode = 'BACTX'
		improvestrategy = 'BA'
	else:
		# non-iterative strategies
		initialquerymode = querystrategy
		# this improvestrategy will not be used for non-iterative strategies
		improvestrategy = 'BA'

	# this is used for parallel search, ignore currently
	accountidx = 0

	while True:
		rounds += 1

		print('=== ROUND [%s] start ===' % (rounds))

		query_record = iterative_workflow(rounds, maxiterations, initialquerymode, accountidx, model, language, target, funcsig, improvestrategy, disablevalidation, outputjson)

		if not disablevalidation:
			if query_record.hasAcceptableResults():
				print('=== ROUND [%s] has generated valid fuzz driver, exit ===' % (rounds))
				break

		if rounds >= maxrounds:
			print('=== Max rounds reached, exit ===')
			break

def main():
	if not cfgs.check_and_load_cfgs():
		print('[ERROR] cfgs check failed, exit')
		exit(1)

	# parse args
	parser = argparse.ArgumentParser(description='fuzzdrivergpt, a GPT-based fuzz driver generator.')
	parser.add_argument('-l', '--language', required=True, choices=['c'], help='language')
	parser.add_argument('-m', '--model', required=True, choices=['gpt-4-0314', 'gpt-4-0613', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-0301'], help='supported GPT models')
	parser.add_argument('-t', '--target', required=True, help='target project')
	parser.add_argument('-f', '--funcsig', required=True, help='function signature')
	parser.add_argument('-q', '--querystrategy', required=True, choices=['NAIVE', 'BACTX', 'DOCTX', 'UGCTX', 'ITER-BA', 'ITER-ALL'], help='supported query strategies')
	parser.add_argument('-DV', '--disablevalidation', required=False, action='store_true', help='whether do validation')
	parser.add_argument('-MI', '--maxiterations', required=False, type=int, default=1, help='maximum iterations for iterative query strategies')
	parser.add_argument('-MR', '--maxrounds', required=False, type=int, default=1, help='maximum rounds for the search process, default is one-round')
	parser.add_argument('-o', '--outputjson', required=True, help='template name for output jsons')
	parser.set_defaults(workflow=None)

	args = parser.parse_args()

	language = args.language
	model = args.model
	target = args.target
	funcsig = args.funcsig
	querystrategy = args.querystrategy
	disablevalidation = args.disablevalidation
	maxiterations = args.maxiterations
	maxrounds = args.maxrounds
	outputjson = args.outputjson

	# check args
	if not outputjson.endswith('.json'):
		print('output json must end with .json')
		exit(1)

	if disablevalidation:
		if maxiterations != 1:
			print('disablevalidation can only be set when maxiterations is 1')
			exit(1)
		elif maxrounds != 1:
			print('disablevalidation can only be set when maxrounds is 1')
			exit(1)
		elif (querystrategy == 'ITER-BA') or (querystrategy == 'ITER-ALL'):
			print('disablevalidation can only be set when querystrategy is not iterative')
			exit(1)

	if maxiterations != 1:
		if (querystrategy != 'ITER-BA') and (querystrategy != 'ITER-ALL'):
			print('maxiterations can only be set when querystrategy is iterative')
			exit(1)

	print('=== Running fuzzdrivergpt ===')

	print('-' * 30)
	print('Language:           %s' % (language))
	print('Model:              %s' % (model))
	print('Target:             %s' % (target))
	print('Func Signature:     %s' % (funcsig))
	print('Query Strategy:     %s' % (querystrategy))
	print('Disable Validation: %s' % (disablevalidation))
	print('Max Iterations:     %s' % (maxiterations))
	print('Max Rounds:         %s' % (maxrounds))
	print('Output Json:        %s' % (outputjson))
	print('-' * 30)

	if os.path.exists(outputjson) and os.path.exists(outputjson.replace('.json', '.pickle')):
		print('Output json already exists, will not continue')
		exit(1)

	if not is_fuzzdrivergpt_image_exist(target):
		print("fuzzdrivergpt image '%s' does not exist, will not continue, please use the following command to build the image first (if it is a supported project):" % (get_fuzzdrivergpt_imgname(target)))
		print('python prepareOSSFuzzImage.py -t fuzzdrivergpt-env %s' % (target))
		exit(1)
	
	main_workflow(language, model, target, funcsig, querystrategy, disablevalidation, maxiterations, maxrounds, outputjson)

if __name__ == '__main__':
	main()
