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
        self.TCP_HOST="streaming2.naad-adna.pelmorex.com"
        self.TCP_IP = socket.gethostbyname( self.TCP_HOST )
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
        self.connected == False
        self.s.close()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        while self.connected == False:
            logger.info("Connecting")
            try: 
                self.s.connect((self.TCP_IP, self.TCP_PORT))
                self.connected = True
            except:
                pass
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

    def _filter_in_geo(self, poly, points):
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

    def filter_in_geo(self, alert, points):
        if not "info" in alert:
            return False
        for infos in alert['info']:
            if isinstance(infos, str):
                if isinstance(alert['info']['area'], OrderedDict):
                    if "polygon" in alert['info']['area']:
                        if isinstance(alert['info']['area']['polygon'], str):
                            return self._filter_in_geo(alert['info']['area']['polygon'], points)
                        else:
                            for polygon in alert['info']['area']['polygon']:
                                return self._filter_in_geo(polygon, points)
                else:
                    logger.error("Geo Filter not implemented: A")
            else:
                if isinstance(infos['area'], OrderedDict):
                    if "polygon" in infos['area']:
                        return self._filter_in_geo(infos['area']['polygon'], points)
                elif isinstance(infos['area'], list):
                    for area in infos['area']:
                        if "polygon" in area:
                            if isinstance(area['polygon'], str):
                                return self._filter_in_geo(area['polygon'], points)
                            else:
                                for polygon in area['polygon']:
                                    return self._filter_in_geo(polygon, points)
                else:
                    logger.error("Geo Filter not implemented: A")

    def parse(self, data):
        alert = xmltodict.parse(data)
        nresult = naadsEvent(alert['alert'])
        return nresult

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
