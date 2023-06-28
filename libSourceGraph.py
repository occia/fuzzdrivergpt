import json
import os
import subprocess
import sys
import time

import logging
logger = logging.getLogger(__name__)

def do_sg_query(api):
    while True:
        try:
            logger.info('  do query for api %s' % (api))
            output = subprocess.check_output(f'src search -json "file:.*\.c lang:c count:all {api}"',shell=True)
            return json.loads(output.decode("utf-8"))

        except Exception as e:
            logger.warning('meet exception when crawling %s' % (e))
            logger.warning('sleep 20s and try again')
            time.sleep(20)

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