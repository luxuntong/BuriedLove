# coding=utf-8
import time
import logging
import json
import heapq
import re
from data import Data
from singleton import singleton
from mqClient.log import log


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

    def getGpsTuple(self):
        return self.longitude, self.latitude


# 单个设备的所有GPS信息池
class GPSPool(list):
    readFile = 'test.html'
    repList = [('ckzlt_mid', lambda gp: gp.getMidStr()),
               ('ckzlt_points', lambda gp: gp.getPointsStr())]

    def __init__(self, topic, devId, owner, isWrite=True):
        self.devId = devId
        self.keys = set()
        self.minLatitude = 9999
        self.minLongitude = 9999
        self.maxLatitude = 0
        self.maxLongitude = 0
        self._funcs = {}
        self._repeat = 0
        print('will open1')
        self.isWrite = isWrite
        if self.isWrite:
            self._fw = open(topic.replace('/', '_') + '.' + devId, 'w')
        print('open2')
        self.isFull = False
        self._topic = topic
        self._owner = owner

    def addData(self, data, isWrite=True):
        gps = GPS(data)
        if gps.key in self.keys:
            self._repeat += 1
            if self._repeat == 5:
                print('repeat beyond 5:', self._repeat)
                if self.isWrite:
                    self._fw.close()
                self.isFull = True
                log('devFull:{}, {}'.format(self._topic, self.devId))
                self._owner.devFull(self._topic, self.devId)
            elif self._repeat > 5:
                print('-' * 30)
            return
        if self.isWrite:
            self._fw.write(data + '\n')
        self.keys.add(gps.key)
        heapq.heappush(self, gps)
        self._notify()

    def register(self, name, func):
        if name in self._funcs:
            print('Error: name in notify:', name)
            return

        self._funcs[name] = func

    def _notify(self):
        for func in self._funcs.values():
            func(self.getSortData())

    # 返回按照时间戳排序的gps信息队列
    def getSortData(self):
        return heapq.nsmallest(len(self), self)

    def getAverageSpeed(self):
        speed = 0
        count = 0
        for gps in self:
            speed += gps.speed
            count += 1

        return speed / count

    def getAverageHigh(self):
        high = 0
        count = 0
        for gps in self:
            high += gps.altitude
            count += 1

        return high / count

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
        self._topics = {}
        # self._initData()
        self._browser = None
        self._mos = None
        self._fullSet = set()
        self._topic = None

    def setBrowser(self, browser, mos):
        self._browser = browser
        self._browser.setMqtt(self)
        self._mos = mos

    def doMosFunc(self, funcName, args):
        getattr(self._mos, funcName)(*args)

    def _initData(self):
        jsons = Data().getDatas()
        for data in Data().getDatas():
            jsonStr = data['data']
            if not jsonStr:
                continue
            print(jsonStr)

            self.setInfo(jsonStr, False)

    def getDevId(self, jsonStr):
        pat = re.compile(r'"devId":\s?"(\w+)"')
        find = pat.search(jsonStr)
        return find.group(1)

    def setAllData(self, jsons):
        for data in jsons:
            print('get json:', data)
            jsonStr = data['data']
            self.setInfo(jsonStr)

    def getKey(self, devId):
        return self._topic + '.' + devId

    def setInfo(self, topic, jsonStr, isWrite=True):
        self._topics.setdefault(topic, {})
        topicDict = self._topics[topic]
        devId = self.getDevId(jsonStr)
        if devId not in topicDict:
            self.addNewPool(topic, devId)
        topicDict[devId].addData(jsonStr, isWrite)

    def addNewPool(self, topic, devId):
        self._topics.setdefault(topic, {})
        topicDict = self._topics[topic]
        topicDict.setdefault(devId, GPSPool(topic, devId, self))
        self._browser.addDevId(devId)

    def devFull(self, topic, devId):
        key = topic + '.' + devId
        self._fullSet.add(key)
        if self.isAllFull():
            self._browser.mqttAllFull()

    def isAllFull(self):
        poolCount = 0
        for topicDict in self._topics.values():
            poolCount += topicDict

        log('is full pcount:{}, fullset:{}'.format(poolCount, len(self._fullSet)))
        return poolCount == len(self._fullSet)

    '''
    def generateHtml(self):
        for pool in self.GPSPools.values():
            pool.generateHtml()
    '''
    def getDev(self, topic, devId):
        topicDict = self._topics.get(topic)
        if not topicDict:
            return None

        return topicDict.get(devId)

    def register(self, topic, devId, name, func):
        dev = self.getDev(topic, devId)
        if not dev:
            logging.ERROR('Error: could register:', topic, devId)
            return

        dev.register(name, func)
