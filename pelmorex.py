#!/usr/bin/env python3

import colorlog
import logging
import pynaads
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)
p = pynaads.naads(passhb=False)

def run():
    p.connect()
    p.start()

    while True:
        item = p.getQueue()
        if item != False:
            if p.filter_in_geo(item, (44.389355, -79.690331)):
                logger.info(item)
            else:
                logger.info(item)
                logger.info("Non-Local event")

def testA():
    testdata = open("samples/6example_CAPCP_with_free_drawn_polygon.xml","r").read()
    item = p.parse(testdata)
    print("Return Fail: {}".format(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625))))
    print("Return Return 1: {}".format(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))))
    for q in item:
        print(q)

def testB(): 
    testdata = open("samples/014B55A1-6609-FCA2-BD91-A582E1EBCEF1.xml","r").read()
    item = p.parse(testdata)
    print("Should Fail: {}".format(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))))
    print("Return Return 1: {}".format(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625))))
    for q in item:
        print(q)

def testC():
    testdata = open("samples/urn:oid:2.49.0.1.124.2651896163.2018.xml","r").read()
    item = p.parse(testdata)
    print("Should Fail: {}".format(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))))
    print("Return Return 1: {}".format(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625))))
    for q in item:
        print(q)

def testD():
    testdata = open("samples/707363CA-611B-BDDF-0494-A276829793D1.xml","r").read()
    item = p.parse(testdata)
    print("Should Fail: {}".format(p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))))
    print("Return Return 1: {}".format(p.filter_in_geo(item, (72.02227211437801, -125.25787353515625))))
    for q in item:
        print(q)

def testAll():
    directory = os.fsencode("savedata")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        testdata = open("savedata/{}".format(filename),"r").read()
        item = p.parse(testdata)
        print (filename)
        p.filter_in_geo(item, (51.5072466571743, -99.22714233398436))

#testA()
#testB()
#testC()
#testD()
#testAll()
run()
