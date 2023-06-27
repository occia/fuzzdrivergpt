import os
import re
import sys
import json
import pickle
import random
import subprocess

import clang.cindex

import libVR
import libImproveQueryGen
import libManualAPIDoc
from libTarget import TargetCfg

cpp_func_decls = [
	clang.cindex.CursorKind.FUNCTION_DECL,
#	clang.cindex.CursorKind.CXX_METHOD,
#	clang.cindex.CursorKind.CONSTRUCTOR,
#	clang.cindex.CursorKind.DESTRUCTOR,
	clang.cindex.CursorKind.CONVERSION_FUNCTION,
]

permissive_acc_specs = [
	clang.cindex.AccessSpecifier.INVALID,
	clang.cindex.AccessSpecifier.PUBLIC,
	clang.cindex.AccessSpecifier.NONE,
]

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

def gen_NAIVE_queries(cfg, funcs, to_chatgpt):
	queries = []

	for mangled_name, info in funcs.items():
		# naive context generation
		fullname = info['fullname']
		path = info['header']
		include = '#include "%s"' % (get_include_path(path, cfg.headers[path]))
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

def gen_XXBACTX_queries(cfg, funcs, to_chatgpt, mode):
	queries = []

	for mangled_name, info in funcs.items():
		# basic context generation

		# 1. infer includes
		#
		# only include the directly related file
		path = info['header']
		include = '#include "%s"' % (get_include_path(path, cfg.headers[path]))
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

		brief_comment, raw_comment = info['brief_comment'], info['raw_comment']

		# 3. tail
		fullname = info['fullname']
		# this is for cpp
		#tail = '// the following function fuzzes %s\nextern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)
		# this is for c
		tail = '// the following function fuzzes %s\nextern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)

		query = '\n\n'.join([include, func_decl, tail])
		if mode == 'DOCTX':
			if raw_comment == 'None':
				if cfg.target in libManualAPIDoc.apidocs:
					if mangled_name in libManualAPIDoc.apidocs[cfg.target]:
						raw_comment = libManualAPIDoc.apidocs[cfg.target][mangled_name]

			if raw_comment != 'None':
				query = '\n\n'.join([include, raw_comment, func_decl, tail])
			else:
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

def fully_qualified(c):
    if c is None:
        return ''
    elif c.kind == clang.cindex.CursorKind.TRANSLATION_UNIT:
        return ''
    else:
        res = fully_qualified(c.semantic_parent)
        if res != '':
            return res + '::' + c.spelling
    return c.spelling

def traverse(source, node, func_list):
	global cpp_func_decls, permissive_acc_specs

	for child in node.get_children():
		if str(child.location.file) == source:
			if child.kind in cpp_func_decls:
				# find the api funcs
				if child.access_specifier in permissive_acc_specs: 
					#print(' -> %s %s %s %s %s %s %s' % (child.spelling, child.displayname, child.mangled_name, child.access_specifier, child.get_usr(), child.brief_comment, child.raw_comment))
					#print(' -> %s %s %s %s %s' % (child.mangled_name, child.access_specifier, child.extent, child.brief_comment, child.raw_comment))
					func_list.append({
						'header': source,
						'mangled_name': str(child.mangled_name), 
						'access': str(child.access_specifier),
						'extent': ((child.extent.start.file.name, child.extent.start.line, child.extent.start.column, child.extent.start.offset), (child.extent.end.file.name, child.extent.end.line, child.extent.end.column, child.extent.end.offset)),
						'brief_comment': str(child.brief_comment),
						'raw_comment': str(child.raw_comment),
						'fullname': fully_qualified(child),
						'args': [ (arg.type.spelling, arg.spelling) for arg in child.get_arguments() ],
						'ret': child.result_type.spelling,
					})

				continue

			elif child.is_abstract_record():
				#elif child.kind == clang.cindex.CursorKind.CLASS_DECL or child.kind == clang.cindex.CursorKind.STRUCT_DECL:
				# don't collect the methods from abstract structs/classes
				continue

			traverse(source, child, func_list)

def refine_list_using_header_analysis(cfg, funcs):
	func_list = []

	print('cfg.headers: %s' % (cfg.headers))

	for header in cfg.headers.keys():
		if not (header.endswith('.h') or header.endswith('.hpp')):
			# currently we skip c++ template header files
			print('[WARN] skip unknown files inside header %s' % (header))
			continue

		print('parse header: %s %s' % (' '.join(cfg.compileopts), header))
		#print('%s %s' % (' '.join(cfg.compileopts), header))
		#os.system('%s -Xclang -ast-dump %s' % (' '.join(cfg.compileopts), header))
		index = clang.cindex.Index.create()
		tu = index.parse(header, cfg.compileopts)
		root = tu.cursor
		traverse(header, root, func_list)

	print('func_list len is %s' % (len(func_list)))
	# filter the func not in the list of funcs provided by nm (not filtered currently)
	filtered_funcs = {}
	funcs = set(funcs)
	for func in func_list:
		## the following is to find the intersection, which has some issues such as the mangled name for an API may have multiple version based on the compiler etc
		#if func['mangled_name'] in funcs:
		#	filtered_funcs[func['mangled_name']] = func
		## the following is just use all found func parsed from header

		blocked = False
		for blocklist in cfg.apiblocklist:
			if re.search(blocklist, func['mangled_name']) != None:
				blocked = True

		if len(func['args']) == 0:
			# API filtering
			# we ignore the apis whose have no argument at all (which means normally we cannot feed input via fuzz driver)
			blocked = True

		if not blocked:
			filtered_funcs[func['mangled_name']] = func

	return filtered_funcs

def find_exported_func_sig_list(binaries):
	apis = set()
	for binary in binaries:
		#print(binary)
		res = subprocess.run(["nm", "--no-demangle", "--defined-only", "-g", binary],
			check=True, capture_output=True, text=True)

		for line in res.stdout.splitlines():
			tokens = line.strip().split()
			if len(tokens) != 3:
				continue
			if tokens[1] == "T":
				apis.add(tokens[2])

	return list(sorted(apis))

def run_antlr_analysis(inpath):
	outfile = '/tmp/antlr_result.json'
	para = os.cpu_count()

	antlr_env = { **os.environ }
	if BaseAnalyzer.is_fuzzdrivergpt_java_prepared():
		antlr_env['JAVA_HOME'] = '/root/workspace/fuzzdrivergpt/jdk-19.0.2'
		antlr_env['PATH'] = '/root/workspace/fuzzdrivergpt/jdk-19.0.2/bin:' + antlr_env['PATH']

	cmd = 'java -Xms1024m -Xmx4096m -Dfile.encoding=UTF-8 -jar /tmp/cc-func-parser-0.5-jar-with-dependencies.jar %s %s %s ALL' % (inpath, para, outfile)

	print('antlr analysis cmd is %s' % (cmd))

	proc = subprocess.Popen(cmd, env=antlr_env, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = proc.communicate()
	ret = proc.returncode

	print("OUT: %s" % (out))
	print("ERR: %s" % (err))

	if ret != 0:
		raise Exception('ret of antlr_analysis is %s' % (ret))

	obj = None
	with open(outfile, 'r') as f:
		obj = json.load(f)
	
	#os.unlink(outfile)
	
	return obj

def get_apis_fuzzed_by_ossfuzz_drivers(cfg, api_funcs):
	if cfg.language == 'c':
		fuzzed_apis, fuzzed_funcs = {}, set([])
		for driver in cfg.known_drivers:
			rslt = run_antlr_analysis(driver)
			for caller in rslt[0]["function_list"]:
				callees = set(caller['callee_func'])
				fuzzed_funcs.update(callees)
	
		for func in fuzzed_funcs:
			if func in api_funcs:
				# we are in c language now, therefore the signature equals to the function name
				fuzzed_apis[func] = api_funcs[func]

		return fuzzed_apis
	else:
		raise Exception('unsupported language %s' % (cfg.language))

def get_file_ctnt(filename, startline, endline):
	print('filename is %s' % (filename))
	with open(filename, 'rb') as f:
		raw_ctnt = f.read(-1)
		ctnt = raw_ctnt.decode('utf-8', errors='ignore')
		lines = ctnt.split('\n')
		return '\n'.join(lines[startline - 1: endline])

def merge_usages(api_usages_list):
	merged_usages = {}

	tmp_dict = {}

	for api_usages in api_usages_list:
		for callee, info_list in api_usages.items():
			for filename, funcname, funcctnt, involved_all_apis in info_list:

				if callee not in tmp_dict:
					tmp_dict[callee] = {}
				if (filename, funcname) not in tmp_dict:
					tmp_dict[callee][(filename, funcname)] = []
			
				has_similar = False
				for exist_funcctnt, _ in tmp_dict[callee][(filename, funcname)]:
					sim = get_jaccard_sim(exist_funcctnt, funcctnt)
					if sim >= 0.9:
						has_similar = True
			
				if not has_similar:
					tmp_dict[callee][(filename, funcname)].append( (funcctnt, involved_all_apis) )
	
	for callee, info in tmp_dict.items():
		if callee not in merged_usages:
			merged_usages[callee] = []

		for k, v in info.items():
			filename, funcname = k
			for e in v:
				funcctnt, involved_all_apis = e
				merged_usages[callee].append( (filename, funcname, funcctnt, involved_all_apis) )

	return merged_usages

def get_usage_functions(cfg, fuzzed_apis, all_apis):
	api_usages = {}

	src_dir = '/src'
	rslts = run_antlr_analysis(src_dir)
	for rslt in rslts:
		if is_existing_fuzz_drivers(cfg, rslt['file_path'], rslt):
			continue

		# exclude the exsiting fuzz drivers
		for caller in rslt['function_list']:
			callees = set(caller['callee_func'])
			involved_fuzz_apis = list(callees.intersection(set(fuzzed_apis.keys())))
			involved_all_apis = list(callees.intersection(set(all_apis.keys())))
			for callee in involved_fuzz_apis:
				# found a function calls an API function
				if callee not in api_usages:
					api_usages[callee] = []
				# cut the function content
				filename = rslt['file_path']
				funcname = caller['function_name']
				funcctnt = get_file_ctnt(filename, caller['line_start'], caller['line_stop'])
				api_usages[callee].append( (filename, funcname, funcctnt, involved_all_apis) )

	return api_usages

def get_jaccard_sim(str1, str2): 
	a = set(str1.split()) 
	b = set(str2.split())
	c = a.intersection(b)
	if len(a) == 0 and len(b) == 0 and len(c) == 0:
		return 1
	else:
		return float(len(c)) / (len(a) + len(b) - len(c))

def is_existing_fuzz_drivers(cfg, filename, antlr_rslt):
	# exactly match name, suitable for local usage check in fuzzdrivergpt:env 
	if filename in cfg.known_drivers:
		return True

	# for usage crawled from sourcegraph
	# is a fuzz driver
	if 'LLVMFuzzerTestOneInput' in antlr_rslt['function_list']:
		return True

	# same file name and high similiarity of file content
	filecnt = ''
	with open(filename, 'rb') as f:
		raw_filecnt = f.read(-1)
		filecnt = raw_filecnt.decode('utf-8', errors='ignore')

	for driver in cfg.known_drivers:
		with open(driver, 'r') as g:
			drivercnt = g.read(-1)
			sim = get_jaccard_sim(filecnt, drivercnt)
			if sim >= 0.9:
				return True

	return False

def get_sourcegraph_usage_functions(cfg, fuzzed_apis, all_apis):
	api_usages = {}

	merged_results = {}

	# get merged search results
	with open(cfg.sgusagejson) as f:
		proj = cfg.target

		obj = json.load(f)
		if proj in obj:
			recorded_for_similarity_check = {}

			for api in fuzzed_apis:
				if api not in obj[proj]:
					continue

				info = obj[proj][api]
				#for result in info['Results'][:1000]:
				for result in info['Results']:
					repo_name = result['repository']['name']
					file_path = result['file']['path']
					file_name = os.path.basename(file_path)

					result_id = os.path.join(repo_name, file_path)
					result_cnt = result['file']['content']

					is_dup = False

					if file_name in recorded_for_similarity_check:
						if result_id in recorded_for_similarity_check[file_name]:
							is_dup = True
						else:
							for result_id in recorded_for_similarity_check[file_name]:
								cnt = merged_results[result_id]
								sim = get_jaccard_sim(cnt, result_cnt)
								if sim >= 0.9:
									is_dup = True
									break
					else:
						recorded_for_similarity_check[file_name] = set([])

					if not is_dup:
						recorded_for_similarity_check[file_name].add(result_id)
						merged_results[result_id] = result_cnt

	if len(merged_results) == 0:
		return api_usages

	# dump the merged results to files
	tmpdir = '/tmp/sourcegraph_tmpdir'
	if os.path.exists(tmpdir):
		os.rmdir(tmpdir)
	os.mkdir(tmpdir)
	for filepath, content in merged_results.items():
		fullpath = os.path.join(tmpdir, filepath)
		dirname = os.path.dirname(fullpath)
		#print('-----')
		#print('the dirname is %s' % (dirname))
		#print('-----')
		os.makedirs(dirname, exist_ok=True)

		with open(fullpath, 'w') as f:
			f.write(content)

	# search usage using antlr in files
	antlr_rslts = run_antlr_analysis(tmpdir)

	for rslt in antlr_rslts:
		if is_existing_fuzz_drivers(cfg, rslt['file_path'], rslt):
			# exclude the exsiting fuzz drivers
			continue

		for caller in rslt['function_list']:
			callees = set(caller['callee_func'])
			involved_fuzz_apis = list(callees.intersection(set(fuzzed_apis.keys())))
			involved_all_apis = list(callees.intersection(set(all_apis.keys())))
			for callee in involved_fuzz_apis:
				# found a function calls an API function
				if callee not in api_usages:
					api_usages[callee] = []
				# cut the function content
				filename = rslt['file_path']
				funcname = caller['function_name']
				funcctnt = get_file_ctnt(filename, caller['line_start'], caller['line_stop'])
				api_usages[callee].append( (filename, funcname, funcctnt, involved_all_apis) )

	return api_usages

def gen_usageid(all_usage_files, all_usage_funcs, usage_file, usage_func):
	all_usage_files = set(all_usage_files)

	parts = usage_file.split('/')
	shortname = None
	for i in range(len(parts) - 1, 0, -1):
		shortname = '/'.join(parts[i:])
		count = 0
		for file in all_usage_files:
			if file.endswith(shortname):
				count = count + 1
		if count == 1:
			break
		
	if shortname == None:
		shortname = usage_file

	return "%s-%s" % (shortname, usage_func)

def gen_XXUGCTX_queries(cfg, fuzzed_apis, all_apis, api_usages, to_chatgpt):
	queries = []

	for mangled_name, info in fuzzed_apis.items():
		# infer includes
		path = info['header']
		INCLUDE = '#include "%s"' % (get_include_path(path, cfg.headers[path]))

		# gen tail
		fullname = info['fullname']
		# this is for c
		TAIL = '// the following function fuzzes %s based on the above API usages\nextern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {\n' % (fullname)

		# 2. for each usage, generate the query
		if mangled_name in api_usages:
			all_usage_files = [ api_usage[0] for api_usage in api_usages[mangled_name] ]
			all_usage_funcs = [ api_usage[1] for api_usage in api_usages[mangled_name] ]

			top_k = 10
			random.shuffle(api_usages[mangled_name])

			for api_usage in api_usages[mangled_name][:top_k]:
				filename, funcname, funcctnt, involved_all_apis = api_usage
				usageid = gen_usageid(all_usage_files, all_usage_funcs, filename, funcname)
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
					apiinfo = all_apis[api]
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

class BaseAnalyzer:

	def __init__(self, cfg):
		self.cfg = cfg
		self.reset()

	def del_if_exist(self, filename):
		if os.path.exists(filename):
			os.remove(filename)

	def reset(self):
		self.del_if_exist(self.cfg.queryfile)

	@staticmethod
	def is_fuzzdrivergpt_java_prepared():
		return os.path.exists('/root/workspace/fuzzdrivergpt/jdk-19.0.2')

	def setup_java_env_for_antlr(self):
		if not self.is_fuzzdrivergpt_java_prepared():
			ret = os.system('apt update')
			if ret != 0:
				raise Exception('`apt update` error with ret %s' % (ret))
			ret = os.system('apt install default-jre -y')
			if ret != 0:
				raise Exception('`apt install default-jre -y` error with ret %s' % (ret))

	def analyze_impl(self, queryMode, params):
		past_query, solution_idx, to_chatgpt = None, None, None

		if queryMode == 'IMPROVE':
			past_query, solution_idx, aaInfo = params['query'], params['solutionIdx'], params['aaInfo']
		elif queryMode != 'ANALYZE':
			to_chatgpt = params['toChatGpt']

		funcsig = params['funcsig'] if 'funcsig' in params else None

		if queryMode == 'NAIVE':
			#
			# phase one: we get the api list
			#
			# 1. find exported func sig list using nm
			#funcs = find_exported_func_sig_list(self.cfg.binaries)
			#print(funcs)
			funcs = []

			# 2. filter the list using header analysis, currently we cover:
			#      - c-style APIs
			#      - public apis of classes 
			#      - currently we didn't include the C++ template functions
			api_funcs = refine_list_using_header_analysis(self.cfg, funcs)
			#print(api_funcs)

			fuzzed_apis = { funcsig : api_funcs[funcsig] } if funcsig in api_funcs else {}

			#
			# phase two: we generate the query of api
			#
			# 3. generate queries of different degrees of diversity of query context 
			queries = gen_NAIVE_queries(self.cfg, fuzzed_apis, to_chatgpt)

			return queries

		elif queryMode == 'BACTX' or queryMode == 'SMKTST' or queryMode == 'DOCTX':
			#
			# phase one: we get the api list
			#
			# 1. find exported func sig list using nm
			#funcs = find_exported_func_sig_list(self.cfg.binaries)
			#print(funcs)
			funcs = []

			# 2. filter the list using header analysis, currently we cover:
			#      - c-style APIs
			#      - public apis of classes 
			#      - currently we didn't include the C++ template functions
			api_funcs = refine_list_using_header_analysis(self.cfg, funcs)
			#print(api_funcs)

			fuzzed_apis = None
			if queryMode == 'BACTX' or queryMode == 'DOCTX':
				fuzzed_apis = { funcsig : api_funcs[funcsig] } if funcsig in api_funcs else {}
			elif queryMode == 'SMKTST':
				fuzzed_apis = api_funcs

			#
			# phase two: we generate the query of api
			#
			# 3. generate queries of different degrees of diversity of query context 
			queries = gen_XXBACTX_queries(self.cfg, fuzzed_apis, to_chatgpt, queryMode)

			return queries

		elif queryMode == 'UGCTX':
			# 0. install the deps
			self.setup_java_env_for_antlr()

			# 1. get api list using header analysis, currently we cover:
			#      - c-style APIs
			#      - public apis of classes 
			#      - currently we didn't include the C++ template functions
			api_funcs = refine_list_using_header_analysis(self.cfg, [])

			# 2. get api list fuzzed in existing ossfuzz drivers
			#fuzzed_apis = get_apis_fuzzed_by_ossfuzz_drivers(self.cfg, api_funcs)
			fuzzed_apis = { funcsig : api_funcs[funcsig] } if funcsig in api_funcs else {}

			# 3. get functions used these apis
			api_usages = get_usage_functions(self.cfg, fuzzed_apis, api_funcs)

			# 4. generate usage-ctx queries
			queries = gen_XXUGCTX_queries(self.cfg, fuzzed_apis, api_funcs, api_usages, to_chatgpt)

			return queries

		elif queryMode == 'SGUGCTX':
			# 0. install the deps
			self.setup_java_env_for_antlr()

			# 1. get api list using header analysis, currently we cover:
			#      - c-style APIs
			#      - public apis of classes 
			#      - currently we didn't include the C++ template functions
			api_funcs = refine_list_using_header_analysis(self.cfg, [])

			# 2. get fuzzing target apis from benchmarkapis.json
			fuzzed_apis = { funcsig : api_funcs[funcsig] } if funcsig in api_funcs else {}

			# 3. get functions used these apis
			api_usages = get_sourcegraph_usage_functions(self.cfg, fuzzed_apis, api_funcs)

			# 4. generate usage-ctx queries
			queries = gen_XXUGCTX_queries(self.cfg, fuzzed_apis, api_funcs, api_usages, to_chatgpt)

			return queries

		elif queryMode == 'ALLUGCTX':
			# 0. install the deps
			self.setup_java_env_for_antlr()

			api_funcs, api_usages = None, None
			if os.path.exists(self.cfg.apicachepickle):
				obj = pickle.load(open(self.cfg.apicachepickle, 'rb'))
				api_funcs, api_usages = obj['api_funcs'], obj['api_usages']
				
			else:

				# 1. get api list using header analysis, currently we cover:
				#      - c-style APIs
				#      - public apis of classes 
				#      - currently we didn't include the C++ template functions
				api_funcs = refine_list_using_header_analysis(self.cfg, [])

				# 2. get functions used these apis
				api_sg_usages = get_sourcegraph_usage_functions(self.cfg, api_funcs, api_funcs)
				api_self_usages = get_usage_functions(self.cfg, api_funcs, api_funcs)
				api_usages = merge_usages( [ api_sg_usages, api_self_usages ] )

				# 3. save as cache for future use 
				pickle.dump({'api_funcs': api_funcs, 'api_usages': api_usages}, open(self.cfg.apicachepickle, 'wb'))

			# 3. get fuzzing target apis from benchmarkapis.json
			fuzzed_apis = { funcsig : api_funcs[funcsig] } if funcsig in api_funcs else {}

			# 4. generate usage-ctx queries
			queries = gen_XXUGCTX_queries(self.cfg, fuzzed_apis, api_funcs, api_usages, to_chatgpt)

			return queries

		elif queryMode == 'IMPROVE':
			api_funcs, api_usages = None, None

			if aaInfo:
				# 0. install the deps
				self.setup_java_env_for_antlr()

				if os.path.exists(self.cfg.apicachepickle):
					obj = pickle.load(open(self.cfg.apicachepickle, 'rb'))
					api_funcs, api_usages = obj['api_funcs'], obj['api_usages']
				
				else:
					# 1. get api list using header analysis, currently we cover:
					#      - c-style APIs
					#      - public apis of classes 
					#      - currently we didn't include the C++ template functions
					api_funcs = refine_list_using_header_analysis(self.cfg, [])

					# 2. get functions used these apis
					api_sg_usages = get_sourcegraph_usage_functions(self.cfg, api_funcs, api_funcs)
					api_self_usages = get_usage_functions(self.cfg, api_funcs, api_funcs)
					api_usages = merge_usages( [ api_sg_usages, api_self_usages ] )

					# 3. save as cache for future use 
					pickle.dump({'api_funcs': api_funcs, 'api_usages': api_usages}, open(self.cfg.apicachepickle, 'wb'))

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
			print(errVR._desc)
			queries = libImproveQueryGen.genImprovedQueries(errVR, code, cut_code, aaInfo, api_funcs, api_usages) 

			return queries

		elif queryMode == 'ANALYZE':
			# 0. install the deps
			self.setup_java_env_for_antlr()

			# get all api funcs list
			funcs = []
			api_funcs = None
			if os.path.exists(self.cfg.apicachepickle):
				obj = pickle.load(open(self.cfg.apicachepickle, 'rb'))
				api_funcs, _ = obj['api_funcs'], obj['api_usages']
			
			else:
				api_funcs = refine_list_using_header_analysis(self.cfg, funcs)
			
			# get all called apis in the driver using antlr
			fuzzed_apis, fuzzed_funcs = {}, set([])
			rslt = run_antlr_analysis('/tmp/analyze_target_driver.c')
			for caller in rslt[0]["function_list"]:
				callees = set(caller['callee_func'])
				fuzzed_funcs.update(callees)

			for func in fuzzed_funcs:
				if func in api_funcs:
					# we are in c language now, therefore the signature equals to the function name
					fuzzed_apis[func] = api_funcs[func]

			with open('/tmp/analyze_result.json', 'w') as f:
				json.dump(list(fuzzed_apis.keys()), f, indent=2, sort_keys=True)

def main():
	pickleCfg, queryMode, paramfile = sys.argv[1], sys.argv[2], sys.argv[3]

	# load cfg
	cfg = TargetCfg.pickleFrom(pickleCfg)

	# load param
	params = None
	with open(paramfile, 'rb') as f:
		params = pickle.load(f)

	# analyze
	analyzer = BaseAnalyzer(cfg)
	queries = analyzer.analyze_impl(queryMode, params)

	# dump
	with open(cfg.queryfile, 'w') as f:
		json.dump(queries, f, indent=2, sort_keys=True)

if __name__ == '__main__':
	main()