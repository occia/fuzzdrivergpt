import os
import re
import sys
import json
import pickle
import random
import subprocess

import clang.cindex

from libTarget import TargetCfg

from validation import libVR
from generation import libImproveQueryGen

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

def refine_list_using_header_analysis(cfg):
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
	# filter the func not in the block list
	filtered_funcs = {}
	for func in func_list:
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

def get_file_ctnt(filename, startline, endline):
	print('filename is %s' % (filename))
	with open(filename, 'rb') as f:
		raw_ctnt = f.read(-1)
		ctnt = raw_ctnt.decode('utf-8', errors='ignore')
		lines = ctnt.split('\n')
		return '\n'.join(lines[startline - 1: endline])

def merge_example_usages(api_usages_list):
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

def get_usage_functions(cfg, analyzed_apis, all_apis):
	api_usages = {}

	src_dir = '/src'
	rslts = run_antlr_analysis(src_dir)
	for rslt in rslts:
		if is_existing_fuzz_drivers(cfg, rslt['file_path'], rslt):
			continue

		# exclude the exsiting fuzz drivers
		for caller in rslt['function_list']:
			callees = set(caller['callee_func'])
			involved_analyze_apis = list(callees.intersection(set(analyzed_apis.keys())))
			involved_all_apis = list(callees.intersection(set(all_apis.keys())))
			for callee in involved_analyze_apis:
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

def get_sourcegraph_usage_functions(cfg, analyzed_apis, all_apis):
	api_usages = {}

	merged_results = {}

	# get merged search results
	with open(cfg.sgusagejson) as f:
		proj = cfg.target

		obj = json.load(f)
		if proj in obj:
			recorded_for_similarity_check = {}

			for api in analyzed_apis:
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
			involved_analyze_apis = list(callees.intersection(set(analyzed_apis.keys())))
			involved_all_apis = list(callees.intersection(set(all_apis.keys())))
			for callee in involved_analyze_apis:
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

class BaseAnalyzer:

	def __init__(self, cfg):
		self.cfg = cfg
		self.reset()

	def del_if_exist(self, filename):
		if os.path.exists(filename):
			os.remove(filename)

	def reset(self):
		self.del_if_exist(self.cfg.projanaresult)

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

	def analyze_impl(self, params):
		# 0. install the deps
		self.setup_java_env_for_antlr()

		# 1. get params
		funcsig = params['funcsig'] if 'funcsig' in params else None

		# 2. get APIs need to be analyzed
		analyzed_apis = {}
		#    + find exported func sig list using nm (useful in binary scenario, currently no use)
		#funcs = find_exported_func_sig_list(self.cfg.binaries)
		#print(funcs)
		#    + filter the list using header analysis, currently we cover:
		#      - c-style APIs
		#      - public apis of classes 
		#      - currently we didn't include the C++ template functions
		api_funcs = refine_list_using_header_analysis(self.cfg)
		#print(api_funcs)

		if funcsig != None:
			# if funcsig is specified, we only analyze that API
			analyzed_apis = { funcsig : api_funcs[funcsig] } if funcsig in api_funcs else {}
		else:
			# if not specified, we analyze all APIs found in headers
			analyzed_apis = api_funcs

		# 3. get functions used these apis from the project code
		api_self_usages = get_usage_functions(self.cfg, analyzed_apis, api_funcs)
		api_sg_usages = get_sourcegraph_usage_functions(self.cfg, analyzed_apis, api_funcs)
		api_usages = merge_example_usages( [ api_sg_usages, api_self_usages ] )

		results = {}
		for api_sig, api_info in api_funcs.items():

			# api basics
			results[api_sig] = { 'funcsig': api_sig, 'apiinfo' : api_info, 'apidoc' : [], 'examples' : [] }

			# api doc
			if api_info['raw_comment'] != 'None':
				results[api_sig]['apidoc'].append(api_info['raw_comment'])

			# api example snippets
			if api_sig in api_usages:
				results[api_sig]['examples'].extend(api_usages[api_sig])

		return results

def main():
	pickleCfg, paramfile = sys.argv[1], sys.argv[2]

	# load cfg
	cfg = TargetCfg.pickleFrom(pickleCfg)

	# load param
	params = None
	with open(paramfile, 'rb') as f:
		params = pickle.load(f)

	# analyze
	analyzer = BaseAnalyzer(cfg)
	results = analyzer.analyze_impl(params)

	# dump
	with open(cfg.projanaresult, 'w') as f:
		json.dump(results, f, indent=2, sort_keys=True)

if __name__ == '__main__':
	main()