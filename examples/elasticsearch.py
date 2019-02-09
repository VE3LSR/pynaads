#!/usr/bin/env python3

import colorlog
import logging
from pynaads import pynaads
import json
from elasticsearch import Elasticsearch

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
p = pynaads.naads(passhb=False)

def run():
    p.connect()
    p.start()
    es = Elasticsearch("http://10.0.10.41:9200")

    while True:
        item = p.getQueue()
        if item != False:
            for q in item:
                if p.filter_in_geo(q, (44.389355, -79.690331)):
                    q['local-event'] = True
                    logger.info(item)
                else:
                    q['local-event'] = False
                    logger.info("Non-Local event")
                es.index(index="naads", body=q, doc_type="_doc")
run()
