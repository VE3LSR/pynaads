import hashlib
import crcmod
import json
import logging
from collections import OrderedDict
from geojson import Polygon, MultiPolygon

logger = logging.getLogger("naads.event")

copyEvent = ['@xmlns', 'identifier', 'Signature', 'msgType', 'note', 'references', 'restriction', 'scope', 'sender', 'sent', 'source', 'status']
crc_func = crcmod.predefined.mkCrcFun('crc-32')

def combine(dictionaries):
    combined_dict = {}
    if isinstance(dictionaries, list):
        for dictionary in dictionaries:
                combined_dict.setdefault(dictionary['valueName'], []).append(dictionary['value'])
    elif isinstance(dictionaries, OrderedDict):
            combined_dict.setdefault(dictionaries['valueName'], []).append(dictionaries['value'])
    return combined_dict

def convertGeo(data):
    data = [tuple(map(float,s.split(','))) for s in data.split(' ')]
    data = [(t[1], t[0]) for t in data] 
    return [data]

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

class naadsBase(dict):
    def __str__(self):
        return self.toJSON()

    def reprJSON(self):
        return dict(self.__dict__)

    def toJSON(self):
        return json.dumps(self.reprJSON(), cls=ComplexEncoder)

class naadsArea(naadsBase):
    def __init__(self, info):
        for name, data in info.items():
            if name == 'geocode':
                self[name] = combine(data)
            elif name == 'areaDesc':
                self[name] = data
            elif name == 'polygon':
                self[name] = data
                if isinstance(data, str):
                    if ' ' not in data:
                        logger.error("Bad Polygon")
                        return None
                    self['location'] = Polygon(convertGeo(data))
                elif isinstance(data, list):
                    polydict = []
                    for poly in data:
                        polydict.append(convertGeo(poly))
                    self['location'] = MultiPolygon(polydict)
                else:
                    self['location'] = {'type': 'unsupported'}
                    logger.error("Unsupported type of polygon area: {}".format(type(data)))
#            elif name == 'circle':
                # <circle>51.507709,-99.233116 2.26</circle>
                # There is no GeoJSON Cicle types, thus needs to be converted to a polygon of sides
            else:
                logger.error("Unsupported Geo Type: {}".format(name))
#        print(self['location'])

class naadsInfo(naadsBase):
    def __init__(self, info):
        if "area" in info:
            self['area'] = []
        for name, data in info.items():
            if name == "area":
                if isinstance(data, OrderedDict):
                    self['area'].append(naadsArea(data))
                elif isinstance(data, list):
                    for area in data:
                        self['area'].append(naadsArea(area))
                else:
                    logger.error("Unknown area type: {}".format(type(data)))
            elif name == "eventCode" or name == "parameter":
                self[name] = combine(data)
            else:
                self[name] = data

class naadsEvent(naadsBase):
    info = 0
    area = 0
    # Create the event class
    def __init__(self, event, ignore=['Signature']):
        self.event = {}
        for c in copyEvent:
            if c in event and c not in ignore:
                self.event[c] = event[c]
        if 'info' in event:
            self.event['info'] = []
            if isinstance(event['info'], OrderedDict):
                self.event['info'].append(naadsInfo(event['info']))
            elif isinstance(event['info'], list):
                for eachInfo in event['info']:
                    if isinstance(eachInfo, OrderedDict):
                        self.event['info'].append(naadsInfo(eachInfo))
                    else:
                        logger.error("Unknown event info list type: {}".format(type(eachInfo)))
            else:
                logger.error("Unknown event info type: {}".format(type(event['info'])))

    # Begin an itterator, set start of iter
    def __iter__(self):
        self.info = 0
        self.area = 0
        return self

    # Get current item, and increase counter
    def __next__(self):
        result = {}
        if 'info' in self.event:
            if self.info >= len(self.event['info']):
                raise StopIteration
            for key, value in self.event.items():
                if key != 'info':
                    result[key] = value
                else:
                    if 'area' in value[self.info]:
                        for akey, avalue in value[self.info].items():
                            if akey != 'area':
                                result[akey] = avalue
                            else:
                                result.update(avalue[self.area])
                    else:
                        result['info'] = value[self.info]
            self.area += 1
            if self.area >= len(self.event['info'][self.info]['area']):
                self.info += 1
                self.area = 0
            return self.genIDs(result)
        else:
            raise StopIteration

    # Get specific item in the list
    def __getitem__(self, key):
        pass

    # Return the length of all the items
    def __len__(self):
        pass

    def genIDs(self, event):
        # IDs must be generated using the following:
        # - identifier
        # - Language
        # and one or more of the following:
        # - polygon
        # - geocode.profile:CAP-CP:Location:0.3 
        # - geocode.layer:EC-MSC-SMC:1.0:CLC
        # If this is not possible, error!
        finalcode = ""
        gotLoc = False
        if 'identifier' in event:
            finalcode += event['identifier']
        else:
            logger.error("Event has no identifier")
        if 'language' in event:
            finalcode += event['language']
        else:
            logger.error("Event has no language")
        if 'polygon' in event:
            if isinstance(event['polygon'], str):
                finalcode += event['polygon']
            elif isinstance(event['polygon'], list):
                for a in event['polygon']:
                    finalcode += a
            gotLoc = True
        if 'geocode' in event: 
            if 'layer:EC-MSC-SMC:1.0:CLC' in event['geocode']:
                finalcode += ''.join(str(e) for e in event['geocode']['layer:EC-MSC-SMC:1.0:CLC'])
                gotLoc = True
            if 'profile:CAP-CP:Location:0.3' in event['geocode']:
                finalcode += ''.join(str(e) for e in event['geocode']['profile:CAP-CP:Location:0.3'])
                gotLoc = True
        if gotLoc == True:
            event['id'] = hashlib.sha256(finalcode.encode()).hexdigest()
            event['search_id'] = '{:x}'.format(crc_func(finalcode.encode()))
        else:
            logger.error("Event does not have specific enough details for uniq ID")
        return event
