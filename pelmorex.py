#!/usr/bin/env python3

import colorlog
import logging
import pynaads
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
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

def testAll():
    d = "sample/download"
#    d = "sample/broken"
#    d = "samples"
    directory = os.fsencode(d)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        testdata = open("{}/{}".format(d, filename),"r").read()
        logger.info(filename)
        item = p.parse(testdata)
        if item != False:
            for q in item:
#                p.filter_in_geo(q, (51.5072466571743, -99.22714233398436))
                p.filter_in_clc(q, "018200")

def test(file, pointA=None, pointB=None, codeA=None, codeB=None):
    testdata = open(file,"r").read()
    item = p.parse(testdata)
    if pointA and pointB:
        print("Should Fail: {}".format(p.filter_in_geo(item, pointA)))
        print("Return Return 1: {}".format(p.filter_in_geo(item, pointB)))

#    if codeA and codeB:
#        print("Should Return 1: {}".format(p.filter_in_clc(item, codeA)))
#        print("Should Fail: {}".format(p.filter_in_clc(item, codeB)))

    for q in item:
        if pointA and pointB:
            print("Item Point: Should Fail: {}".format(p.filter_in_geo(q, pointA)))
            print("Item Point: Return Return 1: {}".format(p.filter_in_geo(q, pointB)))
        if codeA and codeB:
            zones = {'018200': "1"}
            if q['geocode']['layer:EC-MSC-SMC:1.0:CLC'][0] in zones:
                zone = zones[q['geocode']['layer:EC-MSC-SMC:1.0:CLC'][0]]
            else:
                zone = ""
            print (q['geocode']['layer:EC-MSC-SMC:1.0:CLC'][0])
            print("{}: {} - {}".format(q['msgType'], q['areaDesc'], q['headline']), 'WXZ{}'.format(zone))
            print("Item Code: Should Return 1: {}".format(p.filter_in_clc(q, codeA)))
            print("Item Code: Should Fail: {}".format(p.filter_in_clc(q, codeB)))
            pass

#        print(q)


#test("samples/6example_CAPCP_with_free_drawn_polygon.xml", (72.02227211437801, -125.25787353515625), (51.5072466571743, -99.22714233398436))
#test("samples/014B55A1-6609-FCA2-BD91-A582E1EBCEF1.xml", (51.5072466571743, -99.22714233398436), (72.02227211437801, -125.25787353515625))
#test("samples/urn:oid:2.49.0.1.124.2651896163.2018.xml", pointA=(51.5072466571743, -99.22714233398436), pointB=(72.02227211437801, -125.25787353515625))
#test("samples/urn:oid:2.49.0.1.124.2651896163.2018.xml", codeA='018200', codeB='999999')
#test("samples/1.xml")
#test("samples/urn:oid:2.49.0.1.124.2651896163.2018.xml", codeA=['018200'], codeB=['999999'])
#test("samples/707363CA-611B-BDDF-0494-A276829793D1.xml", (51.5072466571743, -99.22714233398436), (72.02227211437801, -125.25787353515625))

#for i in range(10000):
testAll()
#run()
