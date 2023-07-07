import os
import sys
import json
import time
import subprocess

import logging
logger = logging.getLogger(__name__)

import cfgs

def do_sg_query(api):
    while True:
        try:
            logger.info('  do query for api %s' % (api))
            # WARN: it usually fails when we want to crawl all usages, just leave it as 500 for now
            #count_limit = 'all'
            count_limit = '500'
            output = subprocess.check_output(f'src search -json "file:.*\.c lang:c count:{count_limit} {api}"',shell=True, env=dict(os.environ, SRC_ACCESS_TOKEN=cfgs.FDGPT_SOURCEGRAPH_APIKEY))
            return json.loads(output.decode("utf-8"))

        except Exception as e:
            logger.warning('meet exception when crawling %s' % (e))
            logger.warning('sleep 20s and try again')
            time.sleep(20)

def crawl_sg_usage(proj, apis, outfile):
    query_result = {}

    if os.path.exists(outfile):
        with open(outfile, 'r') as f:
            query_result = json.load(f)

    if proj not in query_result:
        query_result[proj] = {}

    for api in apis:
        if api in query_result[proj]:
            logger.info('skip already crawled api (%s, %s)' % (proj, api))
            continue

        query_result[proj][api] = do_sg_query(api)

    with open(outfile, 'w') as f:
        json.dump(query_result, f, indent=2, sort_keys=True)

def main():
    query_result = {}

    #proj = sys.argv[1]
    #api = sys.argv[2]
    proj = 'bind9'
    api = 'dns_message_parse'

    #
    # test crawl & save 
    #
    logger.info('====== crawling api usage of %s/%s ======' % (proj, api))
 
    query_result = { proj: {} }
    query_result[proj][api] = do_sg_query(api)
    
    with open('./meta/crawled_usage.json', 'w') as f:
        json.dump(query_result, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()