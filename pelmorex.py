#!/usr/bin/env python3

import colorlog
import logging
import pynaads
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
logger.info("Test")
p = pynaads.naads(passhb=True)
#p.connect()
#p.start()

#while True:
#    item = p.getQueue()
#    if item:
#        logger.debug(json.dumps(item))

#testdata = open("samples/6example_CAPCP_with_free_drawn_polygon.xml","r").read()  # Test A
testdata = open("samples/014B55A1-6609-FCA2-BD91-A582E1EBCEF1.xml","r").read()     # Test B
item = p.parse(testdata)
#logger.debug(json.dumps(item))

# print(p.filter_in_geo(item, (44.389355, -79.690331)))
print(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436)))    # Matches Test A
print(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625)))  # Matches Test B
