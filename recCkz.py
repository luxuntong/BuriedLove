import CONST
import math
from mqClient.log import log

class RecCkz(object):
    def __init__(self, dev, index):
        self._dev = dev
        self._rgb = CONST.RGB[index]
        self._rgbPos = self._rgb[0]
        self._gTime = self._rgb[1]
        self._gDur = self._rgb[2]
        self._rDur = self._rgb[3]
        self._wholeDur = self._gDur + self._rDur

    def getAllAngle(self, data):
        start = data[0]
        for gps in data:
            gps.rAngle = self.getAngleGPS(start, gps, self._rgbPos)

    def getHashInfo(self, data, func, keyFunc):
        hashInfo = {}
        for gps in data:
            key = func(gps)
            key = keyFunc(key)
            hashInfo[key] = hashInfo.get(key, 0) + 1

        return hashInfo

    def anaFunc(self, x):
        return int(x // 10)

    def calc(self):
        data = self._dev.getSortData()
        self.getAllAngle(data)
        hashInfo = self.getHashInfo(data, lambda gps: gps.rAngle, self.anaFunc)
        print(hashInfo)
        cutList = self.cut(hashInfo)
        if len(cutList) == 1:
            return CONST.BHType.hongdeng

        if len(cutList) == 3:
            self.mergeList(cutList)

        if len(cutList) != 2:
            log('ERROR: cutList:{}, {}, {}'.format(cutList, self._dev._topic, self._dev.devId))
            return -1

        finalAngleAver = self.calcAver(cutList[1])
        if finalAngleAver > 330 or finalAngleAver < 30:
            cutList.reverse()
            finalAngleAver = self.calcAver(cutList[1])

        print(cutList, finalAngleAver)
        self.getDir(finalAngleAver)
        lastFirst, firstEnd = self.getMidData(data, cutList)

        ret = self._calcRGB(lastFirst.timestamp, firstEnd.timestamp)
        if self.dir == CONST.DIR.right:
            if ret:
                return CONST.BHType.lvyou
            else:
                return CONST.BHType.hongyou
        elif self.dir == CONST.DIR.left:
            if ret:
                return CONST.BHType.lvzuo
            else:
                return CONST.BHType.hongzuo
        elif self.dir == CONST.DIR.forward:
            if ret:
                # TODO
                return CONST.BHType.lvzhi
            else:
                return CONST.BHType.hongzhi

        log('ERROR not set result')

    def isTimeG(self, timestamp):
        t = timestamp - self._gTime
        t = t % self._wholeDur
        return t < self._gDur

    def getNextR(self, timestamp):
        t = timestamp - self._gTime
        t = t % self._wholeDur
        return timestamp - t + self._gDur

    def _calcRGB(self, st, en):
        if not self.isTimeG(st):
            return False

        nextR = self.getNextR(st)
        if nextR < en:
            return False

        return True



    def mergeList(self, cutList):
        stList = cutList[0]
        enList = cutList[2]
        for st in stList:
            for en in enList:
                if self.isNear(st, en):
                    stList.extend(enList)
                    del cutList[2]
                    return

    def isNear(self, a, b):
        for i in range(-2, 3, 1):
            tmp = (a + 36 + i) % 36
            if tmp == b:
                return True

        else:
            return False

    def getMidData(self, data, cutList):
        stList = cutList[0]
        enList = cutList[1]
        firstEnd = None
        lastFirst = None
        for gps in data:
            anaKey = self.anaFunc(gps.rAngle)
            if anaKey in stList:
                lastFirst = gps
            elif anaKey in enList and not firstEnd:
                firstEnd = gps

        return lastFirst, firstEnd


    def getDir(self, fAver):
        if 250 < fAver <= 330:
            self.dir = CONST.DIR.right
        elif 70 < fAver <= 145:
            self.dir = CONST.DIR.left
        elif fAver > 145 or fAver <= 235:
            self.dir = CONST.DIR.forward
        else:
            log('ERROR: fAver:{}, {}, {}'.format(fAver, self._dev._topic, self._dev.devId))

    def calcAver(self, calcList):
        aver = 0
        count = 0
        for gps in self._dev:
            anaKey = self.anaFunc(gps.rAngle)
            if anaKey in calcList:
                aver += gps.rAngle
                count += 1
        return aver / count

    def cut(self, hashInfo):
        afterCut = []
        piece = []
        lastAdd = -1
        for i in range(0, 36):
            count = hashInfo.get(i, 0)
            if not count:
                continue

            if count < 5:
                continue

            if lastAdd != -1:
                if i - lastAdd > 2:
                    afterCut.append(piece)
                    piece = []

            piece.append(i)
            lastAdd = i

        if piece:
            afterCut.append(piece)

        return afterCut


    def cut1(self, hashInfo):
        afterCut = []
        piece = []
        last = False
        for i in range(18, -1, -1):
            count = hashInfo.get(i, 0)
            if not count:
                continue

            choice = count > 5
            if last != choice:
                if piece:
                    afterCut.append(piece)

                piece = []
                last = choice

            piece.append(i)

        if piece:
            afterCut.append(piece)

        return afterCut

    @classmethod
    def getAngleGPS(cls, start, end, rgbPos):
        angle = cls.getAngle(cls.getVec(end.getGpsTuple(), rgbPos), cls.getVec(start.getGpsTuple(), rgbPos))
        return angle

    @staticmethod
    def getVec(point1, point2):
        return (point1[0] - point2[0], point1[1] - point2[1])

    @staticmethod
    def getAngle(vector1, vector2):
        x1, y1 = vector1
        x2, y2 = vector2
        v1M = (x1 ** 2 + y1 ** 2) ** 0.5
        v2M = (x2 ** 2 + y2 ** 2) ** 0.5
        cosA = (x1 * x2 + y1 * y2) / (v1M * v2M)
        if cosA < -1:
            cosA = -1
        elif cosA > 1:
            cosA = 1

        A = math.acos(cosA)
        angle = A / math.pi * 180
        return angle if (x1 * y2 - x2 * y1) > 0 else 360 - angle

