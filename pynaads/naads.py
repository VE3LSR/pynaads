#!/usr/bin/env python3

from shapely.geometry import Point, Polygon
from datetime import datetime, timedelta
from collections import OrderedDict
# from signxml import XMLVerifier # See Issue 4
import logging
import socket
from threading import Thread
import queue
import xmltodict
from .event import naadsEvent


logger = logging.getLogger("naads.pelmorex")
# logger.setLevel(logging.INFO)

class naads():
    def __init__(self, passhb=False):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.TCP_HOST=["streaming1.naad-adna.pelmorex.com", "streaming2.naad-adna.pelmorex.com"]
        self.TCP_HOST_ID = 0
        self.TCP_PORT=8080
        self.BUFFER_SIZE=4098
        self.data = None
        self.EOATEXT = b"</alert>"
        self.lastheartbeat = datetime.now()
        self.connected = False
        self.passhb = passhb
        self.queue = queue.LifoQueue()

    def _reconnect(self):
        logger.info("Reconnecting")
        self.TCP_HOST_ID = not self.TCP_HOST_ID
        self.connected = False
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        while self.connected == False:
            logger.info("Connecting")
            try: 
                self.TCP_IP = socket.gethostbyname( self.TCP_HOST[self.TCP_HOST_ID] )
                self.s.connect((self.TCP_IP, self.TCP_PORT))
                self.connected = True
            except:
                self.TCP_HOST_ID = not self.TCP_HOST_ID
        self.s.settimeout(10)
        self.lastheartbeat = datetime.now()

    def local_start(self, queue):
        while 1:
            if self.lastheartbeat + timedelta(minutes=2) < datetime.now():
                logger.warn('Missing heartbeat')
                self._reconnect()
            result = self.read()
            if result != False:
                result = self.parse(result)
                if result.event["sender"] != "NAADS-Heartbeat":
                    logger.info('Alert received', extra={'sender': result.event["sender"]})
                    queue.put(result)
                else:
                    logger.debug('Heartbeat received', extra={'sender': result.event["sender"]})
                    if self.passhb:
                        queue.put(result)
                    self.lastheartbeat = datetime.now()

    def getQueue(self):
        if not self.queue.empty():
            return self.queue.get()
        else:
            return False

    def start(self):
        self.worker = Thread(target=self.local_start, args=(self.queue, ))
        self.worker.setDaemon(True)
        self.worker.start()

    # Checks to see if a point is in the alert poly
    # alert: The alert data
    # points: A tuple or a list of tuples consisting of points
    #
    # Returns the first point position within the poly or false

    def _filter_in_geo_event(self, poly, points):
        p = [tuple(map(float,s.split(','))) for s in poly.split(' ')]
        poly = Polygon(p)
        counter = 0
        if all(isinstance(item, tuple) for item in points):
            for point in points:
                counter += 1
                p1 = Point(point[0], point[1])
                if p1.within(poly):
                    return counter
        else:
            p1 = Point(points[0], points[1])
            if p1.within(poly):
                return 1
            else:
                return False

    def _filter_in_geo_area(self, poly, points):
        poly = Polygon(poly)
        if all(isinstance(item, tuple) for item in points):
            for point in points:
                counter += 1
                p1 = Point(point[0], point[1])
                if p1.within(poly):
                    return counter
        else:
            p1 = Point(points[0], points[1])
            if p1.within(poly):
                return 1
            else:
                return False

    def filter_in_clc(self, alert, clc_code):
        if (isinstance(alert, naadsEvent)):
            logger.error("Filtering of full event not supported yet")
            return False
        else:
            if 'geocode' in alert and 'layer:EC-MSC-SMC:1.0:CLC' in alert['geocode']:
                    if isinstance(clc_code, str):
                        if clc_code in alert['geocode']['layer:EC-MSC-SMC:1.0:CLC']:
                            return True
                        else:
                            return False
                    elif isinstance(clc_code, list):
                        for clc in clc_code:
                            if clc in alert['geocode']['layer:EC-MSC-SMC:1.0:CLC']:
                                return True
                        return False


    def filter_in_geo(self, alert, points):
        if (isinstance(alert, naadsEvent)):
            logger.error("Filtering of full event not supported yet")
            return False
        else:
            if 'location' in alert:
                if alert['location']['type'] == 'Polygon':
                    return self._filter_in_geo_area(alert['location']['coordinates'][0], points)
                elif alert['location']['type'] == 'MultiPolygon':
                    counter = 0
                    for area in alert['location']['coordinates']:
                        counter += self._filter_in_geo_area(area[0], points)
                    return counter
                else:
                    logger.error("Filter location type not supported yet - {}".format(alert['location']['type']))
                    return False

    def parse(self, data):
        for attempt in range (5):
            try:
                alert = xmltodict.parse(data)
            except:
                logger.warn("Bad XML? Retrying")
            else:
                nresult = naadsEvent(alert['alert'])
                return nresult
                break
        else:
            logger.error("Bad XML - Unable to parse")
            return False

    def read(self):
        try:
            buffer = self.s.recv(self.BUFFER_SIZE)
        except socket.timeout:
            return False
        except socket.error:
            logger.debug("Socket error", exc_info=True)
            self._reconnect()
            return False

        if self.data == None: 
            self.data = buffer
        else:
            self.data += buffer

        eoa = self.data.find(self.EOATEXT)
        if (eoa != -1):
            xml = self.data[0:eoa + len(self.EOATEXT)]
            self.data = self.data[eoa + len(self.EOATEXT):]
            return xml
        return False
