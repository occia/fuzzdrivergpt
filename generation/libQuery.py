import re
import json
import time

import openai

import cfgs

import logging
logger = logging.getLogger(__name__)

tokenizer = None

'''
API ways to query
'''

token_err_ptrn = '''This model's maximum context length is ([0-9]+) tokens, however you requested ([0-9]+) tokens \(([0-9]+) in your prompt;'''

def doquery(model, query, key, orgid):
	global token_err_ptrn

	has_error = None
	max_tokens = 400
	while True:
		# do query
		try:
			openai.organization = orgid
			openai.api_key = key
			#resp = openai.Completion.create(engine=model, prompt=query, temperature=0.1, max_tokens=max_tokens, n=10)
			resp = openai.ChatCompletion.create(model=model, messages=[
				{"role": "system", "content": "You are a helpful assistant."},
				{"role": "user", "content": query}
			])
			time.sleep(3)
			break

		except Exception as e:
			err = str(e)

			if 'reduce your prompt' in err:
				logger.warning(err)
				matches = re.search(token_err_ptrn, err)

				if matches == None:
					has_error = 'PromptExceedsLimit: err pattern totally not match'
					break

				grps = matches.groups()
				if len(grps) != 3:
					has_error = 'PromptExceedsLimit: err pattern not match exactly'
					break

				max, prompt = int(grps[0]), int(grps[2])
				if prompt > (max - 10):
					has_error = 'PromptExceedsLimit: too long prompt %s to max %s' % (prompt, max)
					break
				
				# we give a second chance by shrinking the max token num of the response
				max_tokens = max - prompt
				continue

			else:
				logger.warning(err)
				time.sleep(10)
				continue

	if has_error != None:
		return {'status': has_error}
	else:
		rslt = {'status':'FinishedNormally'}
		#rslt['solutions'] = [ choice['text'] for choice in resp['choices'] ]
		rslt['solutions'] = [ choice['message']['content'] for choice in resp['choices'] ]
		logger.debug('get %s resp solutions: %s' % (len(rslt['solutions']), rslt['solutions']))
		return rslt

def init_tokenizer():
	global tokenizer

	if tokenizer == None:
		from transformers import GPT2TokenizerFast
		tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

def get_token_num(query):
	global tokenizer

	init_tokenizer()

	return len(tokenizer(query)['input_ids'])

def token_length_exceeded(model, query):
	# token length check
	token_num = get_token_num(query)
	if 'gpt-3.5' in model:
		# leave at least 500 tokens for answer
		return token_num - 3600
	elif 'gpt-4' in model:
		# leave at least 500 tokens for answer
		return token_num - 6000
		#logger.warning('--- query failed by long token num %s, not retry' % (token_num))
	else:
		raise Exception('Not implemented yet')

def shrink_query_usage_if_can(model, query):
	#logger.debug('before shrink: \n%s' % query)

	if token_length_exceeded(model, query) <= 0:
		logger.debug('no need to shrink')
		return query

	# identify usage part
	lines = query.strip().split('\n')
	startidx, endidx = None, None
	for idx in range(len(lines)):
		if startidx == None and lines[idx].startswith('// @ examples of API usage from'):
			startidx = idx
		if startidx != None and endidx == None and lines[idx].startswith('extern') and lines[idx].endswith(';'):
			endidx = idx
			break
	
	if startidx == None or endidx == None or startidx >= endidx:
		logger.debug('failed to shrink since there is no usage part')
		return query
	
	for idx in range(endidx, startidx - 1, -1):
		new_query = '\n'.join(lines[:idx] + lines[endidx:])
		if token_length_exceeded(model, new_query) <= 0:
			logger.debug('shrinked from %s to %s' % (len(query), len(new_query)))
			logger.debug('=======')
			logger.debug('before shrink: \n%s' % (query))
			logger.debug('=======')
			logger.debug('after shrink: \n%s' % (new_query))
			logger.debug('=======')
			return new_query
	
	logger.debug('failed to shrink to the expected size, startidx %s, endidx %s' % (startidx, endidx))
	return query

def resilient_wrapper_query(model, query):
	# token length check
	if token_length_exceeded(model, query) > 0:
		logger.debug('--- query failed by query exceeded maximum length')
		return { 'status': 'ERRLONGQUERY', 'solutions': [ ] }

	return doquery(model, query, cfgs.FDGPT_OPENAI_APIKEY, cfgs.FDGPT_OPENAI_ORGID)
