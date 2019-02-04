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
p = pynaads.naads(passhb=True)
#p.connect()
#p.start()

#while True:
#    item = p.getQueue()
#    if item:
#        logger.debug(json.dumps(item))
#        print(p.filter_in_geo(item, (44.389355, -79.690331)))

def testA():
    testdata = open("samples/6example_CAPCP_with_free_drawn_polygon.xml","r").read()
    item = p.parse(testdata)
    print("Return Fail: {}".format(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625))))
    print("Return Return 1: {}".format(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))))

def testB(): 
    testdata = open("samples/014B55A1-6609-FCA2-BD91-A582E1EBCEF1.xml","r").read()
    item = p.parse(testdata)
    print("Should Fail: {}".format(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))))
    print("Return Return 1: {}".format(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625))))

testA()
testB()
