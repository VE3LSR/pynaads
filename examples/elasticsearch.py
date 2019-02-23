#!/usr/bin/env python3

import colorlog
import logging
import pynaads
import json
import time
from elasticsearch import Elasticsearch

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
p = pynaads.naads(passhb=False)

clcs = ['044110', '044120', '044130', '044440', '044410', '043220', '046520']

def run():
    p.connect()
    p.start()
    es = Elasticsearch("http://10.0.10.41:9200")

    while True:
        time.sleep(0.2)
        item = p.getQueue()
        if item != False:
            esItems = []
            counter = 0
            for q in item:
                q['local-event'] = False
                if p.filter_in_clc(q, clcs):
                    logger.info("Local Event")
                    q['local-event'] = True
                esItems.append({'index': {'_id': q['id']}})
                esItems.append(q)
                counter += 1
            logger.info("Total events: {}".format(counter))
            es.bulk(index="naads", doc_type="_doc", body=esItems)
run()
