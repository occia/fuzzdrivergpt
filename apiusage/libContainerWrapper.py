import os
import json
import docker
import pickle

from libTarget import TargetCfg
from apiusage.libProjAnalyzer import BaseAnalyzer

import cfgs

import logging
logger = logging.getLogger(__name__)

class ContainerAnalyzer(BaseAnalyzer):

	def __init__(self, cfg):
		super().__init__(cfg)
		if not os.path.exists(self.cfg.workdir):
			os.makedirs(self.cfg.workdir, exist_ok=True)
		self.docker = None

	def get_ana_results(self):
		with open(self.cfg.projanaresult, 'r') as f:
			return json.load(f)

	def analyze_wrap(self, params, debug=False):
		if self.cfg.language == 'c':
			TargetCfg.pickleTo(self.cfg, self.cfg.headerpickle)
			with open(self.cfg.headerparampickle, 'wb') as f:
				pickle.dump(params, f)
			#print('@@params are %s' % (str(params)))

			dockercmd = 'python3 /root/workspace/fuzzdrivergpt/apiusage/libProjAnalyzer.py %s %s' % (self.cfg.headerpickle, self.cfg.headerparampickle)
			if debug:
				logger.info(dockercmd)
				dockercmd = 'sleep 10h'

			imagename = self.cfg.imagename

			envs = [
				"PYTHONPATH=/root/workspace/fuzzdrivergpt",
			]

			dockervolumns = [
				'%s:%s' % (self.cfg.workdir, self.cfg.workdir),
				'%s:%s' % (self.cfg.cachedir, self.cfg.cachedir),
				'%s/libTarget.py:/root/workspace/fuzzdrivergpt/libTarget.py' % (cfgs.FDGPT_DIR),
				'%s/apiusage/__init__.py:/root/workspace/fuzzdrivergpt/apiusage/__init__.py' % (cfgs.FDGPT_DIR),
				'%s/apiusage/libProjAnalyzer.py:/root/workspace/fuzzdrivergpt/apiusage/libProjAnalyzer.py' % (cfgs.FDGPT_DIR),
				'%s/apiusage/libAPIDocManualCollector.py:/root/workspace/fuzzdrivergpt/apiusage/libAPIDocManualCollector.py' % (cfgs.FDGPT_DIR),
				'%s/cfgs.py:/root/workspace/fuzzdrivergpt/cfgs.py' % (cfgs.FDGPT_DIR),
			]

			dockervolumns.append("%s:/tmp/cc-func-parser-0.5-jar-with-dependencies.jar" % (cfgs.FDGPT_ANTLR))

			if os.path.exists(cfgs.FDGPT_JDK):
				dockervolumns.append("%s:/root/workspace/fuzzdrivergpt/jdk-19.0.2" % (cfgs.FDGPT_JDK))

			workdir = self.cfg.workdir
			#print('@@@ the working dir is %s' % (self.cfg.workdir))

			# run the docker
			client = docker.from_env()

			try:
				self.docker = client.containers.run(imagename, environment=envs, command=dockercmd, volumes=dockervolumns, working_dir=workdir, privileged=True, remove=False, detach=True)

			except Exception as ex:
				logger.error('meet exception when run docker %s' % (ex))
				raise ex

			if debug:
				logger.info('docker exec -it %s bash' % (self.docker.name))
				os._exit(0)

			self.docker.reload()
			rets = self.docker.wait()
			if rets['StatusCode'] != 0:
				logger.error('>> Container does not start as expected, check the logs inside the docker:\n\n%s\n' % (self.docker.logs().decode('utf-8', errors='ignore')))
				logger.error('>> Stack track outside container:')
				raise Exception('starting container meets error')

			self.docker.remove(force=True)

			logger.debug('analysis result file %s has been created' % (self.cfg.projanaresult))
		else:
			raise Exception('Unsupported language %s' % (self.cfg.language))
