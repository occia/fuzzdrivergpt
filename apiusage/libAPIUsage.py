import os
import json
import logging

logger = logging.getLogger(__name__)

from apiusage.libContainerWrapper import ContainerAnalyzer
from apiusage import libSourceGraph
from apiusage import libAPIDocManualCollector

# this is the interface for building/caching/retrieving the API usage related information
# currently it contains four types of usage information:
# 1. API function basic information defined in the target project
# 2. API function documentation information
# 3. API usage example code snippets

class APIUsage:
	loadedusages = {}

	def __init__(self, funcsig, apiinfo={}, apidoc=[], examples=[]):
		self.funcsig = funcsig
		self.apiinfo = apiinfo
		self.apidoc = apidoc
		self.examples = examples

	@staticmethod
	def getAPIUsages(proj):
		return APIUsage.loadedusages[proj] if proj in APIUsage.loadedusages else {}

	@staticmethod
	def loadAPIUsagesFromFiles(proj, file):
		with open(file, 'r') as f:
			APIUsage.loadedusages[proj] = json.load(f)
		
		return APIUsage.loadedusages[proj]

	@staticmethod
	def buildAPIUsages(targetcfg, funcsig=None, skipsgcrawl=False):
		'''
		if funcsig is None, build all API usages
		'''
		# inputs assume we have:

		# + from the manually built targetcfg:
		# 	- the analysis docker env
		# 	- the source code of the target project
		# 	- the target project's configuration

		# + from the sourcegraph:
		# 	- additional example code snippets

		# 1. inputs collection (check and collect the inputs)
		# 2. usage extraction (analyze and generate api usages in analysis docker env)
		# 3. usage caching (cache the usages in the local storage)
		# both 1 and 2 can be extended for more ways of collection and extraction

		proj = targetcfg.target

		if os.path.exists(targetcfg.apiusagecache):
			logger.info("loading apiusage from cache '%s'" % (targetcfg.apiusagecache))
			return APIUsage.loadAPIUsagesFromFiles(proj, targetcfg.apiusagecache)

		analyzer = ContainerAnalyzer(targetcfg)

		# 1. inputs collection
		if not skipsgcrawl:
			# get api list
			analyzer.analyze_wrap({'anamode': 'listapisfromheaders'}, debug=False)
			apilist = analyzer.get_ana_results()
			if funcsig != None:
				if funcsig not in apilist:
					logger.error('funcsig %s not in apilist' % funcsig)
					exit(1)
				apilist = [ apilist[funcsig] ]
			else:
				apilist = apilist.values()

			# crawl usage snippets from sourcegraph
			libSourceGraph.crawl_sg_usage(proj, apilist, targetcfg.sgusagejson)

		# 2. usage extraction
		analyzer.analyze_wrap({'anamode': 'collectapiusage', 'funcsig': funcsig}, debug=False)

		# 3. update manually collected api doc
		apiusages = []
		with open(targetcfg.apiusagecache, 'r') as f:
			apiusages = json.load(f)

		if proj in libAPIDocManualCollector.manualapidocs:
			for apisig in libAPIDocManualCollector.manualapidocs[proj]:
				if apisig not in apiusages:
					logger.warning('manual api doc for (%s, %s) not found in apiusagecache' % (proj, apisig))
					continue
				apiusages[apisig]['apidoc'].append(libAPIDocManualCollector.manualapidocs[proj][apisig])

		with open(targetcfg.apiusagecache, 'w') as f:
			json.dump(apiusages, f, indent=2, sort_keys=True)
		
		return APIUsage.loadAPIUsagesFromFiles(proj, targetcfg.apiusagecache)
