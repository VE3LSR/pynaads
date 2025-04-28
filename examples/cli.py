#!/usr/bin/env python3

import logging
import pynaads
import json
import time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

try: 
    import colorlog
    handler = logging.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
    logger.addHandler(handler)
except:
    pass

p = pynaads.naads(passhb=True)

clcs = ['044110', '044120', '044130', '044440', '044410', '043220', '046520']

def run():
    logging.info("Starting NAADS connection")
    p.connect()
    p.start()

    logging.info("Starting")
    while True:
        time.sleep(0.2)
        item = p.queue.get()
        logging.debug("Got item from queue")
        if item != False:
            logger.info(item)
            counter = 0
            for q in item:
                q['local-event'] = False
                if p.filter_in_clc(q, clcs):
                    logger.info("Local Event")
                    q['local-event'] = True
                logging.info(q)
                counter += 1
            logger.info("Total events: {}".format(counter))
run()
