import os

def get_proj_dir():
	if not os.path.exists('ossfuzz-targets'):
		print("running directory is not under the project")
		raise Exception("running directory is not under the project")
	
	return os.path.abspath('.')

# base dir
FDGPT_DIR = get_proj_dir()

# tools
FDGPT_JDK = os.path.join(FDGPT_DIR, 'tools', 'jdk-19.0.2')
FDGPT_ANTLR = os.path.join(FDGPT_DIR, 'tools', 'cc-func-parser-0.5-jar-with-dependencies.jar')

# usage
FDGPT_CRAWLED_USAGE = os.path.join(FDGPT_DIR, 'meta', 'crawled_usage.json')

# ossfuzz supports
FDGPT_OSSFUZZ_TARGETS = os.path.join(FDGPT_DIR, 'ossfuzz-targets')

# openai cfg
def get_openai_cfg(cfgfile):
	pairs = {}
	with open(cfgfile, 'r') as f:
		for line in f.readlines():
			line = line.strip()
			if line == '':
				continue
			if line.startswith('#'):
				continue
			k, v = line.split('=')
			pairs[k.strip()] = v.strip()
	
	return pairs['OPENAI_APIKEY'], pairs['OPENAI_ORGID']

FDGPT_OPENAI_CFG = os.path.join(FDGPT_DIR, 'openaikey.txt')
FDGPT_OPENAI_APIKEY, FDGPT_OPENAI_ORGID = None, None

def check_and_load_cfgs():
	global FDGPT_OPENAI_APIKEY, FDGPT_OPENAI_ORGID

	if not os.path.exists(FDGPT_JDK):
		print("[ERROR] jdk '%s' not found" % (FDGPT_JDK))
		return False
	if not os.path.exists(FDGPT_ANTLR):
		print("[ERROR] antlr jar '%s' not found" % (FDGPT_ANTLR))
		return False
	if not os.path.exists(FDGPT_CRAWLED_USAGE):
		print("[ERROR] crawled usage '%s' not found" % (FDGPT_CRAWLED_USAGE))
		return False
	if not os.path.exists(FDGPT_OSSFUZZ_TARGETS):
		print("[ERROR] ossfuzz targets '%s' not found" % (FDGPT_OSSFUZZ_TARGETS))
		return False
	if not os.path.exists(FDGPT_OPENAI_CFG):
		print("[ERROR] openai cfg '%s' not found" % (FDGPT_OPENAI_CFG))
		return False

	FDGPT_OPENAI_APIKEY, FDGPT_OPENAI_ORGID = get_openai_cfg(FDGPT_OPENAI_CFG)
	return True

if __name__ == '__main__':

	print('=== cfgs.py ===')
	print('project dir is %s' % FDGPT_DIR)
	print('jdk dir is %s' % FDGPT_JDK)
	print('antlr jar is %s' % FDGPT_ANTLR)
	print('crawled usage is %s' % FDGPT_CRAWLED_USAGE)
	print('ossfuzz targets dir is %s' % FDGPT_OSSFUZZ_TARGETS)

