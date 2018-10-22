import time
import heapq
def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

class GPS(object):
    def __init__(self, jsonData):
        self.devId = jsonData['devId']
        self.timestamp = jsonData['timestamp']
        self.latitude = jsonData['latitude']
        self.longitude = jsonData['longitude']
        self.satellite = jsonData['satellite']
        self.hdop = jsonData['hdop']
        self.altitude = jsonData['altitude']
        self.speed = jsonData['speed']
        self.direction = jsonData['direction']
        
    def __lt__(self, other):
        return self.timestamp < other.timestamp
        
class GPSPool(list):
    def __init__(self, devId):
        self.devId = devId
    
    def addData(self, data):
        heapq.heappush(self, GPS(data))

@singleton
class MQTT(object):
    def __init__(self, *args, **kwargs):
        self.first = True
        self.GPSPools = {}
    
    def setInfo(self, jsonData):
        devId = jsonData['devId']
        self.GPSPools.setdefault(devId, GPSPool(devId))
        self.GPSPools[devId].addData(jsonData)
        
    def printDiff(self, latitude, longitude, timestamp):
        print(self.first)
        if self.first:
            return
        
        print('-' * 60)
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp)))
        print(timestamp - self.timestamp)
        print(latitude - self.latitude, longitude - self.longitude)