import json
import logging

logger = logging.getLogger(__name__)

from apiusage.libProjAnalyzer import merge_example_usages
from apiusage.libContainerWrapper import ContainerAnalyzer

# this is the interface for building/caching/retrieving the API usage related information
# currently it contains four types of usage information:
# 1. API function basic information defined in the target project
# 2. API function documentation information
# 3. API usage example code snippets

class APIUsage:

	def __init__(self, funcsig, apiinfo={}, apidoc=[], examples=[]):
		self.funcsig = funcsig
		self.apiinfo = apiinfo
		self.apidoc = apidoc
		self.examples = examples

	def update(self, newapiusage):
		if self.funcsig != newapiusage.funcsig:
			logger.ERROR('funcsig mismatch: updating apiusage of %s with %s' % (self.funcsig, apiusage.funcsig))
			exit(1)

		# update apiinfo
		for k, v in newapiusage.apiinfo.items():
			self.apiinfo[k] = v

		# update apidoc
		for doc in newapiusage.apidoc:
			if doc not in self.apidoc:
				self.apidoc.append(doc)

		# update examples
		if len(newapiusage.examples) != 0:
			merged_examples = merge_example_usages([{self.funcsig: self.examples}, {self.funcsig: newapiusage.examples}])
			self.examples = merged_examples[self.funcsig]

	@staticmethod
	def buildAPIUsages(targetcfg, funcsig=None):
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

		# 1. inputs collection
		# usage snippets from sourcegraph
		pass

		# 2. usage extraction
		analyzer = ContainerAnalyzer(targetcfg)
		analyzer.analyze_wrap({'funcsig': funcsig}, debug=False)

		results = None
		with open(targetcfg.projanaresult, 'r') as f:
			results = json.load(f)

		apiusages = []
		for api_sig, api_info in results.items():
			apiusages.append(APIUsage(api_sig, api_info['apiinfo'], api_info['apidoc'], api_info['examples']))

		return apiusages
