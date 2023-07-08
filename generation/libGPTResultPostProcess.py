import sys
import json

def handleSingleResult(query_rslt):
	if 'CHATGPT' not in query_rslt['id']:
		return
	if 'result' not in query_rslt:
		return
	if 'status' not in query_rslt['result']:
		return
	if query_rslt['result']['status'] != 'FinishedNormally':
		return
	if 'valiations' in query_rslt['result']:
		raise Exception('this is a validation result, not a query result')

	raw_solutions = []
	if 'raw_solutions' in query_rslt['result']:
		raw_solutions = query_rslt['result']['raw_solutions']
	else:
		raw_solutions = query_rslt['result']['solutions']

	fixed_solutions = []
	if 'IMPROVE' in query_rslt['id']:
		for raw_solution in raw_solutions:
			# TODO: fix answers of more languages
			# identify things wrapped by ```
			find_all = lambda _str,_w : [ i for i in range(len(_str)) if _str.startswith(_w,i) ]
			idx_list = find_all(raw_solution, '```')
			if len(idx_list) % 2 != 0:
				idx_list.append(len(raw_solution))
			
			fixed_solution = '// FAILED TO FIX'
			code_list = [ raw_solution[idx_list[i]:idx_list[i+1]] for i in range(0, len(idx_list), 2) ]
			for code in code_list:
				if 'LLVMFuzzerTestOneInput' in code:
					if code.startswith('```c'):
						fixed_solution = code.replace('```c', '')
					else:
						fixed_solution = code.replace('```', '')

			fixed_solutions.append(fixed_solution)
	else:
		for raw_solution in raw_solutions:
			# TODO: fix answers of more languages
			fixed_solution = raw_solution.replace('```c', '').replace('```', '').strip()
			fixed_solutions.append(fixed_solution)

	query_rslt['result']['raw_solutions'] = raw_solutions
	query_rslt['result']['solutions'] = fixed_solutions

def handleGPTResult(input):
	for query_rslt in input:
		handleSingleResult(query_rslt)

if __name__ == '__main__':
	inputjson = sys.argv[1]

	input = None
	with open(inputjson, 'r') as f:
		input = json.load(f)
		handleGPTResult(input)

	with open(inputjson, 'w') as f:
		json.dump(input, f, indent=2, sort_keys=True)
