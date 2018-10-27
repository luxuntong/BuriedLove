import CONST
import math

class RecCkz(object):
    def __init__(self, dev, index):
        self._dev = dev
        self._rgb = CONST.RGB[index]

    def calc(self):
        data = self._dev.getSortData()
        start = data[0]
        end = data[-1]
        rgbPos = self._rgb[0]
        angle = self.getAngle(self.getVec(end.getGpsTuple(), rgbPos), self.getVec(rgbPos, start.getGpsTuple()))
        print(angle)

    @classmethod
    def getAngleGPS(cls, start, end, rgbPos):
        angle = cls.getAngle(cls.getVec(end.getGpsTuple(), rgbPos), cls.getVec(rgbPos, start.getGpsTuple()))
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
        return A / math.pi * 180

