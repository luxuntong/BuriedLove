import cord_convert as cc
from math import *
from mqtt import GPS
import numpy

# gpsLocationListOrderByTs type is list, item is a dict
# 
def behaviorRecog(gpsLocationListOrderByTs,  ledGpsInfo):
    led_tuple = ledGpsInfo[0][0] # get rgb led loc
    near_list = getNearLedGpsList(gpsLocationListOrderByTs, led_tuple, 100)
    pos, _ = getNearestPos(near_list, led_tuple)
    pec = isPeccancy(near_list[pos].timestamp, ledGpsInfo)
    direction = getPassDirection(near_list[pos+1:], ledGpsInfo)
    if direction == 'b':
        return 7
    elif direction == 's':
        if pec:
            return 3
        else:
            return 6
    elif direction == 'l':
        if pec:
            return 4
        else:
            return 1
    elif direction == 'r':
        if pec:
            return 5
        else:
            return 2


# 是否违章
def isPeccancy(nearTimestamp, ledInfo):
    delta = abs(nearTimestamp - ledInfo[1])
    passSec = delta % (ledInfo[2] + ledInfo[3])
    return passSec <= 40


# 获取过红绿灯后的方向
def getPassDirection(gpsAfterLed, ledInfo, precision=10):
    majority = dict()
    for gps in gpsAfterLed[:precision]:
        majority[getCorrectedDirection(getRelativePointAngle(ledInfo[0], gps.getGpsTuple()))] += 1
    right_direction = 's'
    max = 0
    for direction, num in majority:
        if num > max:
            max = num
            right_direction = direction
    return right_direction




# 获取两点间相对第一点偏向角度，以顺时针计算。
def getRelativePointAngle(relativeLoc1, loc2):
    if relativeLoc1 == (0, 0):
        loc2_relative = loc2
    else:
        loc2_relative = numpy.array([loc2[0] - relativeLoc1[0] + 1, loc2[1] - relativeLoc1[1] + 1])
    loc1_relative = numpy.array([0, 1])
    c = get_cosine(loc1_relative, loc2_relative)
    deg =  get_degrees_from_cossine(c)
    if loc2_relative[0] < 0.0:
        deg = 360.0 - float(floor(deg))
    return deg


# 获取矫正后的方向，
# s 是直行， r 右转， b 调头， l左转
def getCorrectedDirection(angle):
    if angle < 30 or angle > 330:
        return 's'
    elif 30 <= angle < 150:
        return 'r'
    elif 150 <= angle < 210:
        return 'b'
    elif 210 <= angle < 330:
        return 'l'

# 相对于loc1 loc2在loc1的方位
def getQuadrant(loc1, loc2):
    if loc1[0] < loc2[0]:
        if loc1[1] < loc2[1]:
            return 1
        else:
            return 2
    else:
        if loc1[1] > loc2[1]:
            return 3
        else:
            return 4


# 判断是否是朝红绿灯方向
def isRightAngle(direction, quadrant):
    if quadrant == 1:
        return 0.0 < direction <= 90.0
    elif quadrant == 2:
        return 90.0 < direction <= 180.0
    elif quadrant == 3:
        return 180.0 < direction <= 270.0
    elif quadrant == 4:
        return 270.0 < direction <= 360.0
    else:
        return False


def getAdvanceCount(gpsInfo, ledInfo):
    dis = getDistance(gpsInfo.getGpsTuple(), ledInfo)
    if dis > 1000:
        return

# 返回离红绿灯最近的点
def getNearestPos(gpsList, ledLoc):
    nearestPos = 0
    neareat = getDistance(gpsList[0], ledLoc)
    for gps in gpsList[1:]:
        dis = getDistance(gps.getGpsTuple(), ledLoc)
        if neareat > dis:
            neareat = dis
            nearestPos = gpsList.index(2)
    return nearestPos, neareat


# 返回离红绿灯100m以内的点
def getNearLedGpsList(gpsList, led_loc, nearDis):
    nearList = []
    for gps in gpsList:
        dis = getDistance(gps.getGpsTuple(), led_loc)
        # 如果距离离红绿灯小于一定距离
        if dis <= nearDis:
            nearList.append(gps)

    k = lambda d:  d.timestamp
    nearList.sort(key=k)
    return nearList



def getCorrectedCord(long, lat):
    corList = cc.wgs84_to_bd09(long ,lat )
    return corList[0], corList[1]


def getDistance(cord1, cord2):
    def __distance(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
        """
        根据经纬度计算距离
        :param lon1: 点1经度
        :param lat1: 点1纬度
        :param lon2: 点2经度
        :param lat2: 点2纬度
        :return:distance
        """
        # 将十进制度数转化为弧度
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371393 # 地球平均半径，单位为米
        return float('%.2f' % (c * r))
    return __distance(cord1[0], cord1[1], cord2[0], cord2[1])


def get_cosine(v1, v2):
    """ calculate cosine and returns cosine """
    n1 = get_norm_of_vector(v1)
    n2 = get_norm_of_vector(v2)
    ip = get_inner_product(v1, v2)
    return ip / (n1 * n2)


def get_inner_product(v1, v2):
    """ calculate inner product """
    return numpy.dot(v1, v2)


def get_norm_of_vector(v):
    """ calculate norm of vector """
    return numpy.linalg.norm(v)


def get_radian_from_cosine(cos):
    return numpy.arccos(cos)


def get_degrees_from_cossine(cos):
    return numpy.degrees(numpy.arccos(cos))


if __name__ == '__main__':
    print(getCorrectedCord(120.191601, 30.190383))
    print(getCorrectedDirection(45))
