import os
import json
import random

import logging

logger = logging.getLogger(__name__)

from libTarget import TargetCfg

from apiusage import libAPIUsage
from validation import libVR
from generation import libImprovePrompt

def get_include_path(path, prefix):
	path = path.replace(prefix, '')
	if path.startswith('/'):
		path = path[1:]
	return path

def gen_func_declaration(info):
	#ret, fullname, args = info['ret'], info['fullname'], ','.join([ arg[0] for arg in info['args'] ])
	ret, fullname, args = info['ret'], info['fullname'], ','.join([ arg[0] + " " + arg[1] for arg in info['args'] ])

	#if "::" in func_decl:
	#	func_decl = '//' + func_decl

	return 'extern %s %s(%s);' % (ret, fullname, args)

def gen_NAIVE_queries(cfg, targetapis, apiusages, to_chatgpt):
	queries = []

	for apisig in targetapis:
		mangled_name, info = apisig, apiusages[apisig]['apiinfo']

		# naive context generation
		fullname = info['fullname']
		path = info['header']
		include = '#include "%s"' % (get_include_path(path, info['prefix']))
		# this is for cpp
		#tail = '// the following function fuzzes %s\nextern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)
		# this is for c
		tail = '// the following function fuzzes %s\nextern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)

		query = '\n\n'.join([ tail ])

		queryMode = "NAIVE"
		if to_chatgpt:
			query = '// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.\n\n' + query
			queryMode = "NAIVE-CHATGPT"

		queries.append({
			'id': '%s-%s-%s-%s' % (cfg.language, cfg.target, mangled_name, queryMode),
			'language': cfg.language,
			'queryMode': queryMode,
			'query': query,
			'target': cfg.target,
			'info': info,
			'naiveIncluded': include,
		})

		#input('Press ENTER to continue\n')
		#print(query)
	
	return queries

def gen_XXBACTX_queries(cfg, targetapis, apiusages, to_chatgpt, mode):
	queries = []

	for apisig in targetapis:
		mangled_name, info = apisig, apiusages[apisig]['apiinfo']

		# basic context generation

		# 1. infer includes
		#
		# only include the directly related file
		path = info['header']
		include = '#include "%s"' % (get_include_path(path, info['prefix']))
		#sig = '/include/'
		#include = '#include "%s"' % (path[path.find(sig) + len(sig):])

		## includes all headers currently, can do smart infer & include later
		#includes = []
		#for header in cfg.headers:
		#	sig = '/include/'
		#	includes.append( '#include "%s"' % (header[header.find(sig) + len(sig):]) )
		#include = '\n'.join(includes)

		# 2. func declaration
		func_decl = gen_func_declaration(info)

		# 3. tail
		fullname = info['fullname']
		# this is for cpp
		#tail = '// the following function fuzzes %s\nextern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)
		# this is for c
		tail = '// the following function fuzzes %s\nextern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)

		query = '\n\n'.join([include, func_decl, tail])
		if mode == 'DOCTX':
			if ('apidoc' in apiusages[apisig]) and (len(apiusages[apisig]['apidoc']) > 0):
				# randomly choose one doc from given
				doc = random.choice(apiusages[apisig]['apidoc'])
				query = '\n\n'.join([include, doc, func_decl, tail])
			else:
				# we do not generate DOCTX queries if there is no doc
				continue

		if mode == 'SMKTST':
			queryMode = 'SMKTST'
		elif mode == 'BACTX':
			queryMode = "BACTX"
			if to_chatgpt:
				query = '// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.\n\n' + query
				queryMode = "BACTX-CHATGPT"
		elif mode == 'DOCTX':
			queryMode = "DOCTX"
			if to_chatgpt:
				query = '// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.\n\n' + query
				queryMode = "DOCTX-CHATGPT"
		else:
			raise Exception('Unknown mode: %s' % (mode))

		queries.append({
			'id': '%s-%s-%s-%s' % (cfg.language, cfg.target, mangled_name, queryMode),
			'language': cfg.language,
			'queryMode': queryMode,
			'query': query,
			'target': cfg.target,
			'info': info,
		})

		#input('Press ENTER to continue\n')
		#print(query)
	
	return queries

def gen_usageid(example_files, example_funcs, usage_file, usage_func):
	example_files = set(example_files)

	parts = usage_file.split('/')
	shortname = None
	for i in range(len(parts) - 1, 0, -1):
		shortname = '/'.join(parts[i:])
		count = 0
		for file in example_files:
			if file.endswith(shortname):
				count = count + 1
		if count == 1:
			break
		
	if shortname == None:
		shortname = usage_file

	return "%s-%s" % (shortname, usage_func)

def gen_XXUGCTX_queries(cfg, targetapis, apiusages, to_chatgpt):
	queries = []

	for apisig in targetapis:
		mangled_name, info = apisig, apiusages[apisig]['apiinfo']
		examples = apiusages[apisig]['examples'] if 'examples' in apiusages[apisig] else []

		# infer includes
		path = info['header']
		INCLUDE = '#include "%s"' % (get_include_path(path, info['prefix']))

		# gen tail
		fullname = info['fullname']
		# this is for c
		TAIL = '// the following function fuzzes %s based on the above API usages\nextern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)

		# 2. for each usage, generate the query
		#logger.debug(len(examples))
		#logger.debug(examples)
		if len(examples) > 0:
			example_files = [ example[0] for example in examples ]
			example_funcs = [ example[1] for example in examples ]

			# currently we randomly pick top k example
			top_k = 10
			random.shuffle(examples)

			for example in examples[:top_k]:
				filename, funcname, funcctnt, involved_all_apis = example
				usageid = gen_usageid(example_files, example_funcs, filename, funcname)
				# usage func content
				# we try usageid instead of filename to avoid the github repo info for sourcegraph usages
				usage_lines = [ '// @ examples of API usage from %s' % (usageid) ]
				#usage_lines = [ '// @ examples of API usage from %s' % (filename) ]
				for line in funcctnt.split('\n'):
					usage_lines.append("// " + line)
				USAGE = '\n'.join(usage_lines)

				# involved api func declaration
				api_func_decls = []
				for api in involved_all_apis:
					if api in apiusages:
						apiinfo = apiusages[api]['apiinfo']
						api_func_decl = gen_func_declaration(apiinfo)
						api_func_decls.append(api_func_decl)
				FUNC_DECL = '\n'.join(api_func_decls)

				query = '\n\n'.join([INCLUDE, USAGE, FUNC_DECL, TAIL])
				queryMode = "UGC-%s" % (usageid)

				if to_chatgpt:
					query = '// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.\n\n' + query
					queryMode = 'UGC-CHATGPT-%s' %(usageid)

				queries.append({
					'id': '%s-%s-%s-%s' % (cfg.language, cfg.target, mangled_name, queryMode),
					'language': cfg.language,
					'queryMode': queryMode,
					'query': query,
					'target': cfg.target,
					'info': info,
					'usageSrcFile': filename,
					'usageSrcFunc': funcname,
					'usageID': usageid,
				})

				#input('Press ENTER to continue\n')
				#print(query)

	return queries

def genQueries(mode, cfg, params):
	if mode == 'NAIVE':
		targetapis, apiusages, to_chatgpt = params['targetapis'], params['apiusages'], params['to_chatgpt']
		return gen_NAIVE_queries(cfg, targetapis, apiusages, to_chatgpt)

	elif mode == 'BACTX' or mode == 'DOCTX' or mode == 'SMKTST':
		targetapis, apiusages, to_chatgpt = params['targetapis'], params['apiusages'], params['to_chatgpt']
		return gen_XXBACTX_queries(cfg, targetapis, apiusages, to_chatgpt, mode)

	elif mode == 'ALLUGCTX' or mode == 'SGUGCTX' or mode == 'UGCTX':
		targetapis, apiusages, to_chatgpt = params['targetapis'], params['apiusages'], params['to_chatgpt']
		return gen_XXUGCTX_queries(cfg, targetapis, apiusages, to_chatgpt)

	elif mode == 'IMPROVE':
		past_query, solution_idx, apiusages, aa_info = params['past_query'], params['solution_idx'], params['targetapis'], params['apiusages'], params['aa_info']

		validation = past_query['result']['validations'][solution_idx]
		code = validation['code']
		#print(code)
		cut_code = []
		start = False
		for line in code.split('\n'):
			if start:
				cut_code.append(line)
			if line.startswith('// The following is a fuzz driver written in C language') or line.startswith('// Based on the above information, fix the code.'):
				#code.split('// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.\n\n')[1]
				# we use this one to be compatible with the old version prompt
				start = True

		cut_code = '\n'.join(cut_code).strip('\n')

		errVR = libVR.BasicVR.load(validation['vali_result'])
		logger.debug(errVR._desc)
		queries = libImprovePrompt.genImprovedQueries(errVR, code, cut_code, aa_info, fullapis, api_usages) 

		return queries

	else:
		raise Exception('Unknown mode for prompt generation: %s' % (mode))
