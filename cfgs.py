import os
import logging

logger = logging.getLogger(__name__)

def get_proj_dir():
	if not os.path.exists('ossfuzz-targets'):
		logger.error("running directory is not under the project")
		raise Exception("running directory is not under the project")
	
	return os.path.abspath('.')

def load_apikey_cfg(cfgfile):
	pairs = {}
	if not os.path.exists(cfgfile):
		return pairs

	with open(cfgfile, 'r') as f:
		for line in f.readlines():
			line = line.strip()
			if line == '':
				continue
			if line.startswith('#'):
				continue
			k, v = line.split('=')
			pairs[k.strip()] = v.strip()
	
	return pairs

def configure_log(loglevel):
	pass

def init_log():
	logging.config.fileConfig(FDGPT_LOGCONF, disable_existing_loggers=False)

# base dir
FDGPT_DIR = get_proj_dir()
# work dir
FDGPT_WORKDIR = os.path.join(FDGPT_DIR, 'workdir')

# log conf
FDGPT_LOGCONF = os.path.join(FDGPT_DIR, 'logging.conf')

# 3rdparty
FDGPT_JDK = os.path.join(FDGPT_DIR, '3rdparty', 'jdk-19.0.2')
FDGPT_ANTLR = os.path.join(FDGPT_DIR, '3rdparty', 'cc-func-parser-0.5-jar-with-dependencies.jar')

# ossfuzz supports
FDGPT_OSSFUZZ_TARGETS = os.path.join(FDGPT_DIR, 'ossfuzz-targets')

# apikey cfg
FDGPT_APIKEY_FILE = os.path.join(FDGPT_DIR, 'apikey.txt')
FDGPT_OPENAI_APIKEY, FDGPT_OPENAI_ORGID = None, None
FDGPT_SOURCEGRAPH_APIKEY = None

def check_and_load_cfgs(check_openai_keys=True):
	global FDGPT_OPENAI_APIKEY, FDGPT_OPENAI_ORGID, FDGPT_SOURCEGRAPH_APIKEY

	init_log()

	if not os.path.exists(FDGPT_JDK):
		logging.error("jdk '%s' not found" % (FDGPT_JDK))
		return False

	if not os.path.exists(FDGPT_ANTLR):
		logging.error("antlr jar '%s' not found" % (FDGPT_ANTLR))
		return False

	if not os.path.exists(FDGPT_OSSFUZZ_TARGETS):
		logging.error("ossfuzz targets '%s' not found" % (FDGPT_OSSFUZZ_TARGETS))
		return False

	keypairs = load_apikey_cfg(FDGPT_APIKEY_FILE)
	if check_openai_keys:
		if 'OPENAI_APIKEY' not in keypairs or 'OPENAI_ORGID' not in keypairs:
			logging.error("apikey cfg file '%s' does not contain openai keys" % (FDGPT_APIKEY_FILE))
			return False

		FDGPT_OPENAI_APIKEY, FDGPT_OPENAI_ORGID = keypairs['OPENAI_APIKEY'], keypairs['OPENAI_ORGID']

	else:
		logging.info("skip checking openai keys")
	
	if 'SOURCEGRAPH_APIKEY' not in keypairs:
		logging.warning("apikey cfg file '%s' does not contain sourcegraph api key, go get one APIKEY from '%s' to boost the crawling process" % (FDGPT_APIKEY_FILE, 'https://docs.sourcegraph.com/cli/how-tos/creating_an_access_token'))
		FDGPT_SOURCEGRAPH_APIKEY = ''
	else:
		FDGPT_SOURCEGRAPH_APIKEY = keypairs['SOURCEGRAPH_APIKEY']

	return True

if __name__ == '__main__':

	logger.info('=== cfgs.py ===')
	logger.info('project dir is %s' % FDGPT_DIR)
	logger.info('jdk dir is %s' % FDGPT_JDK)
	logger.info('antlr jar is %s' % FDGPT_ANTLR)
	logger.info('ossfuzz targets dir is %s' % FDGPT_OSSFUZZ_TARGETS)

