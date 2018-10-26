import cord_convert as cc
from math import *

# gpsLocationListOrderByTs type is list, item is a dict
# 
def behaviorRecog(gpsLocationListOrderByTs,  ledGpsInfo):
    pass



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


if __name__ == '__main__':
    print(getCorrectedCord(120.191601, 30.190383))