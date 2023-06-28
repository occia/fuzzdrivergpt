import json
import sys

def printDriverCode(jsonfile, qid):
	with open(jsonfile, 'r') as f:
		data = json.load(f)
		info = data[qid]
		#print(info['result']['validations'][0]['code'])
		print(info['result']['solutions'][0])

if __name__ == '__main__':
	jsonfile, qid = sys.argv[1], sys.argv[2]
	printDriverCode(jsonfile, qid)
