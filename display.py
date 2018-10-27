import matplotlib.pyplot as plt
import random
import recCkz
from mqtt import GPSPool
from matplotlib import colors as mcolors
import math
import CONST
import recog
import os

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
sorted_names = [name for hsv, name in by_hsv]
class AnaManager(object):
    def __init__(self):
        self.topics = {}
        self.getTopics()

    def getTopics(self):
        files = os.listdir('data')
        topicSet = set()
        for file in files:
            file = file.split('.')
            if len(file) == 2:
                topicSet.add(file[0])

        topicList = list(topicSet)
        topicList.append('no')
        for topic in topicList:
            self.topics[topic] = Ana(topic)

    def pltTest(self, plt):
        gaoshang = self.topics['no']
        gaoxia = self.topics['GPSLocation_test7_2']
        #gaoshang.pltTest(plt)
        #gaoxia.pltTest(plt)
        topicGP = self.getTopicKey(1)
        topicGP.pltTest(plt)

    def getTopicKey(self, index):
        topicStr = CONST.topic[index]
        topicStr = topicStr.replace('/', '_')
        return self.topics[topicStr]

    def test(self):
        gaoshang = self.topics['no']
        gaoxia = self.topics['GPSLocation_test7_2']
        gaoshang.test()
        print('-' * 30)
        gaoxia.test()
        print('$' * 30)
        gaoshang.anaAll(CONST.dataType.gaojia)
        print('$' * 30)
        gaoxia.anaAll(CONST.dataType.gaojia)
        print(self.topics.keys())
        for index in range(12):
            topicGP = self.getTopicKey(index)
            print('&' * 30)
            print(topicGP._topic)
            topicGP.anaAll(CONST.dataType.xingwei)



class Ana(object):
    def __init__(self, topic, topicDict=None):
        files = os.listdir('data')
        self.GPSPools = {}
        self._topic = topic
        if topicDict:
            self.GPSPools = topicDict
            return

        for name in files:
            if topic == 'no':
                if '.' in name:
                    continue
            else:
                if topic not in name:
                    continue

            self.GPSPools[name] = self.createGP(name)
        
    def createGP(self, filename):
        gp = GPSPool('1', filename, None, False)
        split_char = '/'
        if os.name == 'nt':
            split_char = "\\"
        with open('data' + split_char + filename) as fr:
            for line in fr:
                gp.addData(line)
        return gp
    
    def getData(self, devId):
        return self.GPSPools[devId].getSortData()
    
    def getAllData(self):
        for gp in self.GPSPools.values():
            yield gp.getSortData()

    def anaHash(self, hashLen):
        if hashLen <= 9:
            return CONST.gaojia.xia
        elif hashLen >= 13:
            return CONST.gaojia.shang
        else:
            return CONST.gaojia.notknow

    def anaAll(self, dataType):
        rets = {}
        if dataType == CONST.dataType.gaojia:
            for dev in self.GPSPools.values():
                ret = self.gaojia(dev)
                print(ret)
                rets[dev.devId] = ret

        elif dataType == CONST.dataType.xingwei:
            for dev in self.GPSPools.values():
                print(dev.devId)
                self.rgbAna(dev)
                rets[dev.devId] = 1

        return rets

    def gaojia(self, dev):
        data = dev.getSortData()
        hashLen = self.getHashInfo(data, lambda gps: gps.altitude, round)
        ret = self.anaHash(hashLen)
        if CONST.gaojia.isOK(ret):
            return ret

        avHigh = dev.getAverageHigh()
        if avHigh > 11:
            return CONST.gaojia.shang
        else:
            return CONST.gaojia.xia

    def getHashInfo(self, data, func, keyFunc):
        hashInfo = {}
        for gps in data:
            key = func(gps)
            key = keyFunc(key)
            hashInfo[key] = hashInfo.get(key, 0) + 1

        maxRate = max(hashInfo.values())
        minRate = min(hashInfo.values())
        return len(hashInfo)

    def pltTest(self, plt):
        for index, dev in enumerate(self.GPSPools.values()):
            if index != 0:
                continue

            data = dev.getSortData()

            '''
            x = [gps.longitude for gps in data]
            y = [gps.latitude for gps in data]
            plt.plot(x, y, color=colors[sorted_names[index]])
            plt.scatter(120.191689, 30.189142, color='blue')
            break
            '''
            start = data[0]
            rgbPos = CONST.RGB[0][0]
            x = []
            y = []
            for gps in data:
                x.append(gps.timestamp)
                y.append(recCkz.RecCkz.getAngleGPS(start, gps, rgbPos))
            plt.plot(x, y)
            break

    def test(self):
        for gp in self.GPSPools.values():
            print('devId:{}, avSpeed:{}, avHigh:{}'.format(gp.devId, gp.getAverageSpeed(), gp.getAverageHigh()))

    # ---------------------------------------
    def rgbAna(self, dev):
        topic = self._topic.replace('_', '/')
        index = CONST.topic.index(topic)
        rgb = CONST.RGB[index]
        try:
            print(CONST.ConstBehavior[recog.behaviorRecog(dev.getSortData(), rgb)])
        except IndexError:
            print("Error on ", index)
        # ckz = recCkz.RecCkz(dev, index)
        # return ckz.calc()
        return 1


if __name__ == '__main__':
    am = AnaManager()
    am.test()
    # fig = plt.figure(1, facecolor='white')
    # fig.clf()
    # axl = plt.subplot(111, frameon=False)
    # '''
    # for index, data in enumerate(ana.getAllData()):
    #     x = [gps.timestamp for gps in data]
    #     y = [gps.speed for gps in data]
    #     plt.plot(x, y, color=colors[sorted_names[index]])
    #     '''
    # am.pltTest(plt)
    # plt.show()