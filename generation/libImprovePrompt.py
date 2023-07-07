import os
import random

from validation import libVR

'''
Testing commands:

# ERR-PRSE-DRIVER-Semantic Issue-too few arguments to function call, expected 5, have 3	
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-pjsip-pj_stun_msg_decode-BACTX-CHATGPT

# ERR-PRSE-DRIVER-Parse Issue-expected expression
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-igraph-igraph_read_graph_graphdb-BACTX-CHATGPT

# ERR-PRSE-DRIVER-Semantic Issue-assigning to 'isc_mem_t *' (aka 'struct isc_mem *') from incompatible type 'void'
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-bind9-dns_message_parse-BACTX-CHATGPT

# ERR-LINK-CONFIG-UNDEF-REF-init_sip_msg
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-kamailio-get_src_uri-BACTX-CHATGPT

# ERR-FUZZ-DRIVER-RET-0-NONEFF
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-kamailio-parse_route_headers-BACTX-CHATGPT

# ERR-FUZZ-DRIVER-RET-77-libFuzzer-deadly signal
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-igraph-igraph_read_graph_pajek-BACTX-CHATGPT

# ERR-FUZZ-DRIVER-RET-1-MEMLEAK
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-libdwarf-dwarf_init_path-BACTX-CHATGPT

# ASAN-heap-buffer-overflow
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-libucl-ucl_parser_add_string-BACTX-CHATGPT

# ERR-FUZZ-DRIVER-RET-1-ASAN-stack-buffer-overflow on address XXX	
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-inchi-GetINCHIKeyFromINCHI-BACTX-CHATGPT

# ERR-PRSE-DRIVER-Semantic Issue-use of undeclared identifier 'DNS_RDATACLASS_IN'
python genQueries.py improve -i 0 \
	-v tasks/query_results_validated_BACTX-CHATGPT-3.5-TURBO.json \
	-q c-bind9-dns_master_loadbuffer-BACTX-CHATGPT

'''

def driver_frame_to_line_no(driver_frame):
	#print(driver_frame)
	try:
		return int(driver_frame.split('dummyfuzzer.c')[1].split(':')[1])
	except Exception as e:
		print('Error: cannot get line number from driver frame: %s\n Exception is %s' % (driver_frame, e))
		return 0

def find_relevant_apis(cut_code, errline, api_funcs):
	# - api in err line
	# - if no api in err line, find the closest api from top to down (rough implementation for data dependency)
	start = False
	closest_api = None
	for line in cut_code.split('\n'):
		if errline == line.strip():
			start = True
	
		if start:
			for api in api_funcs.keys():
				# rough measure for calling the api
				if (api + '(') in line:
					return api

	return None

def get_api_info(api_func):
	ret, fullname, args, raw_comment = api_func['ret'], api_func['fullname'], ','.join([ arg[0] + " " + arg[1] for arg in api_func['args'] ]), api_func['raw_comment']

	if raw_comment == 'None':
		return 'extern %s %s(%s);' % (ret, fullname, args)
	else:
		return '%s\nextern %s %s(%s);' % (raw_comment, ret, fullname, args)

def get_example_usages(examples, api):
	if api in examples:
		# TODO: we only pick the first five for now
		all_usages = []
		for filename, _, funcctnt, _ in examples[api][:5]:
			usage_lines = [ '// @ examples of API `%s` usage from %s' % (api, filename) ]
			for line in funcctnt.split('\n'):
				usage_lines.append("// " + line)
			one_usage = '\n'.join(usage_lines)
			all_usages.append(one_usage)
		return all_usages
	else:
		return []

def get_related_infos(cut_code, err_line, aainfo, api_funcs, examples):
	related_infos = [ '' ]
	if aainfo:
		related_api = find_relevant_apis(cut_code, err_line, api_funcs)
		if related_api != None:
			related_api_info = get_api_info(api_funcs[related_api])
			for related_api_usage in get_example_usages(examples, related_api):
				related_info = '\nThe definition of `%s`:\n%s\n\n%s\n\n' % (related_api, related_api_info, related_api_usage)
				related_infos.append(related_info)

	return related_infos

ERR_PRSE_TMPL = '''
```
%s
```

The above C code has compilation error.
The error line is:
%s

The error description is:
%s
%s
Based on the above information, fix the code.
'''

ERR_LINK_TMPL = '''
```
%s
```

The above C code calls a non-existing API %s.
%s
Based on the above information, fix the code.
'''

ERR_FUZZ_MEMLEAK_TMPL = '''
```
%s
```

The above C code can be built successfully but has runtime memory leak.
%s

Based on the above information, fix the code.
'''

ERR_FUZZ_OOM_TMPL = '''
```
%s
```

The above C code can be built successfully but meet out-of-memory, perhaps due to memory leak.
%s

Based on the above information, fix the code.
'''

ERR_FUZZ_TIMEOUT_TMPL = '''
```
%s
```

The above C code can be built successfully but will stuck (timeout).
%s

The frames of the stack are:
%s

%s

Based on the above information, fix the code.
'''

ERR_FUZZ_CRASH_TMPL = '''
```
%s
```

The above C code can be built successfully but will crash (%s).
%s

The frames of the stack are:
%s

%s
%s
Based on the above information, fix the code.
'''

ERR_FUZZ_NONEFF_TMPL = '''
```
%s
```

The above C code can be built successfully but its fuzzing seems not effective since the coverage never change.

Based on the above information, fix the code if necessary.
'''

'''
If the function returns a None, no need to query again for improving it
If the function returns a string, it is the improved query that needs to be queried again
'''
def genImprovedQueries(errVR, code, cut_code, aainfo, apiusages):
	# TODO: handle this type of error later
	#if errVR.ty == 'ERR-CORR'

	api_funcs = { apisig : apiusages[apisig]['apiinfo'] for apisig in apiusages }
	examples = { apisig : apiusages[apisig]['examples'] for apisig in apiusages }

	next_queries = []

	if errVR.ty == 'ERR-PRSE':
		# one type of build error

		# get error line
		lines = code.split('\n')
		line_no = int(errVR._line)
		err_line = lines[line_no - 1].strip()

		# get error description
		err_desc = errVR._desc.strip()

		# TODO: get related information
		for related_info in get_related_infos(cut_code, err_line, aainfo, api_funcs, examples):
			next_query = ERR_PRSE_TMPL % (cut_code, err_line, err_desc, related_info)
			next_queries.append(next_query)
		return next_queries

	elif errVR.ty == 'ERR-LINK':
		# one type of build error

		# get first undefined function
		firstUnknownFunction = errVR._reference

		# TODO: get related information
		err_line = None
		for line in cut_code.split('\n'):
			if (firstUnknownFunction + '(') in line:
				err_line = line.strip()
				break

		for related_info in get_related_infos(cut_code, err_line, aainfo, api_funcs, examples):
			next_query = ERR_LINK_TMPL % (cut_code, firstUnknownFunction, related_info)
			next_queries.append(next_query)
		return next_queries

	elif errVR.ty == 'ERR-FUZZ':
		# runtime error

		# TODO: now only handle the following types of runtime error, for others we do not provide improvement query

		oracle = errVR._oracle
		stacks = errVR._stacks
		lines = code.split('\n')

		if oracle == 'MEMLEAK' or oracle == 'OOM':
			# - mem leak or oom
			driver_frames = set([])
			for stack in stacks:
				for frame in stack:
					if 'dummyfuzzer' in frame:
						driver_frames.add(frame)
						break
			
			driver_line_nos = []
			for frame in driver_frames:
				line_no = driver_frame_to_line_no(frame)
				if line_no != 0:
					driver_line_nos.append(line_no)
			driver_line_nos.sort()

			driver_lines = [ lines[line_no - 1] for line_no in driver_line_nos ]
			
			# TODO: do we have memleak/oom related information to provide?
			if oracle == 'MEMLEAK':
				lines_info = '' if len(driver_lines) == 0 else ( 'The leak related lines of code are:\n' + '\n'.join(driver_lines) )

				next_query = ERR_FUZZ_MEMLEAK_TMPL % (cut_code, lines_info)
				return [ next_query ]

			elif oracle == 'OOM':
				lines_info = '' if len(driver_lines) == 0 else ( 'The out-of-memory related stacks are:\n' + '\n'.join(driver_lines) )

				next_query = ERR_FUZZ_OOM_TMPL % (cut_code, lines_info)
				return [ next_query ]

		elif oracle.startswith('ASAN-') or oracle.startswith('libFuzzer-') or oracle.startswith('UNKNOWN'):
			# - crash/exit/abort/timeout
			stacks_with_driver = set([])
			first_stack = None
			for stack in stacks:
				for frame in stack:
					if 'dummyfuzzer' in frame:
						if first_stack == None:
							first_stack = tuple(stack)

						stacks_with_driver.add(tuple(stack))
						break

			if len(stacks_with_driver) == 0:
				print('WARN: no stacks detected from driver, cannot generate improve query')
				return []
			elif len(stacks_with_driver) != 1:
				print('WARN: found %d stacks with driver, currently we pick the first one' % len(stacks_with_driver))

			#stack_with_driver = random.choice(list(stacks_with_driver))
			stack_with_driver = first_stack

			crash_frames = []
			crash_line_no = 0 
			for frame in stack_with_driver:
				crash_frames.append(frame)
				if 'dummyfuzzer' in frame:
					crash_line_no = driver_frame_to_line_no(frame)
					break

			crash_frames = crash_frames
			code_around_frames = {}
			if aainfo:
				for frame in crash_frames:
					parts = frame.split(' ')
					if len(parts) == 5 and ':' in parts[4]:
						title, location = parts[3], parts[4]
						file, line_no, _ = location.split(':')
						line_no = int(line_no)
						if os.path.exists(file):
							adjusted_lines = []

							with open(file, 'r') as f:
								related_lines = f.readlines()[line_no - 2:line_no + 1]
								for idx in range(len(related_lines)):
									adjusted_lines.append( '%s\t%s' % (line_no - 1 + idx, related_lines[idx].strip()) )

							code_around_frames[title] = '\n'.join(adjusted_lines)

			if 'libFuzzer-timeout after' in oracle:
				# TODO: add related information, do we have for timeout?
				crash_line = '' if crash_line_no == 0 else ( 'The possible stuck line is:\n' + lines[crash_line_no - 1].strip() )
				next_query = ERR_FUZZ_TIMEOUT_TMPL % (cut_code, crash_line, '\n'.join(crash_frames), '\n\n'.join([ 'The frame `%s` related code:\n%s' % (frame_title, frame_code) for frame_title, frame_code in code_around_frames.items() ]))
				return [ next_query ]
			else:
				# TODO: add related information
				if crash_line_no == 0:
					crash_line = ''
					related_info = ''
					next_query = ERR_FUZZ_CRASH_TMPL % (cut_code, oracle, crash_line, '\n'.join(crash_frames), '\n\n'.join([ 'The frame `%s` related code:\n%s' % (frame_title, frame_code) for frame_title, frame_code in code_around_frames.items() ]), related_info)
					return [ next_query ]
				else:
					crash_line = 'The crash line is:\n' + lines[crash_line_no - 1].strip()
					for related_info in get_related_infos(cut_code, lines[crash_line_no - 1].strip(), aainfo, api_funcs, examples):
						next_query = ERR_FUZZ_CRASH_TMPL % (cut_code, oracle, crash_line, '\n'.join(crash_frames), '\n\n'.join([ 'The frame `%s` related code:\n%s' % (frame_title, frame_code) for frame_title, frame_code in code_around_frames.items() ]), related_info)
						next_queries.append(next_query)
					return next_queries

		elif oracle.startswith('NONEFF'):
			# - non-effective at all (cov no change, but this may not be an issue)
			# TODO: do we need to provide related information in improvement query?
			next_query = ERR_FUZZ_NONEFF_TMPL % (cut_code)
			return [ next_query ]

	else:
		return []
