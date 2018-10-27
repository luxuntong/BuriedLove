import cord_convert as cc
from math import *
from mqtt import GPS
import numpy
import dataset
from CONST import *
import json

# gpsLocationListOrderByTs type is list, item is a dict
# 
def behaviorRecog(gpsLocationListOrderByTs,  ledGpsInfo):
    led_tuple = ledGpsInfo[0] # get rgb led loc
    near_list = getNearLedGpsList(gpsLocationListOrderByTs, led_tuple, 100)
    pos, _ = getNearestPos(near_list, led_tuple)
    pec = is_single_peccancy(near_list[pos], ledGpsInfo)
    direction = getPassDirection(near_list[pos+1:], ledGpsInfo)
    w_pos, _ = getNearestLinePos(near_list, led_tuple)
    wait = is_wait_single(near_list[w_pos])
    if wait:
        return 7
    else:
        if direction == 's':
            if pec:
                return 6
            else:
                return 3
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

def is_single_peccancy(gps, ledInfo):
    delta = abs(gps.timestamp - ledInfo[1])
    passSec = delta % (ledInfo[2] + ledInfo[3])
    return passSec > ledInfo[2]

# 是否违章
def isPeccancy(gpsInfoList, ledInfo):
    pec_dict = {True: 0, False:0}
    for gps in gpsInfoList:
        delta = abs(gps.timestamp - ledInfo[1])
        passSec = delta %(ledInfo[2] + ledInfo[3])
        pec_dict[passSec > ledInfo[2]] +=1
    is_pec = True
    max = 0
    for t, n in pec_dict.items():
        if n > max:
            max = n
            is_pec = t

    # 不能 大于等于 因为这时候是穿过红灯的时候
    return is_pec

def is_wait_single(gps):
    return gps.speed == 0.0


def isWaiting(gpsList):
    # true is wating
    speed_dict = {True: 0, False: 0}
    for gps in gpsList:
        if gps.speed > 0.0:
            speed_dict[False] +=1
        else:
            speed_dict[True] += 1
    is_wait = True
    max = 0
    for t, n in speed_dict.items():
        if n > max:
            max = n
            is_wait = t
    return is_wait

# 获取过红绿灯后的方向
def getPassDirection(gpsAfterLed, ledInfo, precision=10):
    majority = {
        'r': 0,
        's': 0,
        'b': 0,
        'l': 0}
    for gps in gpsAfterLed[:precision]:
        # angle = getRelativePointAngle(ledInfo[0], gps.getGpsTuple())
        angle = gps.direction
        key = getCorrectedDirection(angle)
        majority[key] += 1
    right_direction = 's'
    max = 0
    for direction, num in majority.items():
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
    if angle <= 45.0 or angle >= 315.0:
        return 's'
    elif 45.0 < angle <= 180.0:
        return 'r'
    elif 180.0 < angle < 315.0:
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

# 返回离红绿灯线最近的点
def getNearestPos(gpsList, ledLoc):
    if len(gpsList) == 0 :
        raise IndexError
    led_line = 0.0
    nearestPos = 0
    neareat = getDistance(gpsList[0].getGpsTuple(), ledLoc)
    for gps in gpsList[1:]:
        dis = getDistance(gps.getGpsTuple(), ledLoc)
        if neareat > dis:
            neareat = dis
            nearestPos = gpsList.index(gps)
    return nearestPos, neareat

# 返回离红绿灯线最近的点
def getNearestLinePos(gpsList, ledLoc):
    if len(gpsList) == 0 :
        raise IndexError
    led_line = 43.36
    nearestPos = 0
    neareat = getDistance(gpsList[0].getGpsTuple(), ledLoc)
    for gps in gpsList[1:]:
        dis = getDistance(gps.getGpsTuple(), ledLoc)
        dis = fabs(dis - led_line)
        if neareat > dis:
            neareat = dis
            nearestPos = gpsList.index(gps)
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
    db = dataset.connect("sqlite:///gps.db")
    tb = db['GPSLocation/test1/1']
    devices = db.query("select * from 'GPSLocation/test1/1' group by devId;")
    gpsList = list()
    print(getDistance((120.19184666666666, 30.188776666666666),(120.191689, 30.189142)))
    # for d in devices:
    #     for item in tb.find(devId = d['devId']):
    #         gpsList.append(GPS(json.dumps(item)))
    #     ret = behaviorRecog(gpsList, RGB[0])
    #     print(ConstBehavior[ret])
    #     gpsList = list()
    # for item in tb.find(devId = '5D8BDC41'):
    #     gpsdata.append(GPS(json.dumps(item)))
    #
    #
    # ret = behaviorRecog(gpsdata, RGB[0])
    # print(ConstBehavior[ret])

