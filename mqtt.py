# coding=utf-8
import time
import json
import heapq
import re
from data import Data
from singleton import singleton


class GPS(object):
    KEYS = ['timestamp', 'latitude', 'longitude']

    def __init__(self, jsonStr):
        self.generateKey(jsonStr)
        jsonData = json.loads(jsonStr)
        self.devId = jsonData['devId']
        self.timestamp = jsonData['timestamp']
        self.latitude = jsonData['latitude']
        self.longitude = jsonData['longitude']
        self.satellite = jsonData['satellite']
        self.hdop = jsonData['hdop']
        self.altitude = jsonData['altitude']
        self.speed = jsonData['speed']
        self.direction = jsonData['direction']
        self.data = jsonStr

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def generateKey(self, jsonStr):
        pat = re.compile(r'"(\w+)":([^,]+),')
        key = ''
        for m in pat.finditer(jsonStr):
            if m.group(1) in self.KEYS:
                key += m.group(2) + '&'
        self.key = key


# 单个设备的所有GPS信息池
class GPSPool(list):
    readFile = 'test.html'
    repList = [('ckzlt_mid', lambda gp: gp.getMidStr()),
               ('ckzlt_points', lambda gp: gp.getPointsStr())]

    def __init__(self, devId):
        self.devId = devId
        self.keys = set()
        self.minLatitude = 9999
        self.minLongitude = 9999
        self.maxLatitude = 0
        self.maxLongitude = 0

    def addData(self, data):
        gps = GPS(data)
        if gps.key in self.keys:
            return

        self.keys.add(gps.key)
        heapq.heappush(self, gps)
        Data().addData(gps.data)

    # 返回按照时间戳排序的gps信息队列
    def getSortData(self):
        return heapq.nsmallest(len(self), self)

    def getEdgeValue(self):
        for gps in self:
            self.minLatitude = min(self.minLatitude, gps.latitude)
            self.minLongitude = min(self.minLongitude, gps.longitude)
            self.maxLatitude = max(self.maxLatitude, gps.latitude)
            self.maxLongitude = max(self.maxLongitude, gps.longitude)

        self.midLatitude = (self.minLatitude + self.maxLatitude) / 2
        self.midLongitude = (self.minLongitude + self.maxLongitude) / 2

    def getMidStr(self):
        return '{}, {}'.format(self.midLongitude, self.midLatitude)

    def getPointsStr(self):
        points = self.getSortData()
        points = ['new BMap.Point({},{})'.format(
            gps.longitude, gps.latitude) for gps in points]
        return ',\n\t'.join(points)

    def generateHtml2(self):
        self.getEdgeValue()
        with open(self.readFile) as fr:
            fw = open(self.devId + '.html', 'w')
            for line in fr:
                for rep, func in self.repList:
                    if rep in line:
                        line = line.replace(rep, func(self))

                fw.write(line)

    def generateHtml(self):
        self.getEdgeValue()
        with open(self.readFile, encoding='UTF-8') as fr:
            fw = open(self.devId + '.html', 'w')
            data = fr.read()
            for rep, func in self.repList:
                data = data.replace(rep, func(self))
                
            fw.write(data)
            

@singleton
class MQTT(object):
    def __init__(self, *args, **kwargs):
        self.first = True
        self.GPSPools = {}
        self._initData()
        
    def _initData(self):
        jsons = Data().getDatas()
        for data in Data().getDatas():
            jsonStr = data['data']
            if not jsonStr:
                continue 
        
            self.setInfo(jsonStr)

    def getDevId(self, jsonStr):
        pat = re.compile(r'"devId":\s?"(\w+)"')
        find = pat.search(jsonStr)
        return find.group(1)
    
    def setAllData(self, jsons):
        for data in jsons:
            print('get json:', data)
            jsonStr = data['data']
            self.setInfo(jsonStr)            

    def setInfo(self, jsonStr):
        devId = self.getDevId(jsonStr)
        self.GPSPools.setdefault(devId, GPSPool(devId))
        self.GPSPools[devId].addData(jsonStr)

    def generateHtml(self):
        for pool in self.GPSPools.values():
            pool.generateHtml()
