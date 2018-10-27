# -*- coding:utf-8 -*-
import time
topic = ['GPSLocation/test1/1',
         'GPSLocation/test1/2',
         'GPSLocation/test2/1',
         'GPSLocation/test2/2',
         'GPSLocation/test3/1',
         'GPSLocation/test3/2',
         'GPSLocation/test4/1',
         'GPSLocation/test4/2',
         'GPSLocation/test5/1',
         'GPSLocation/test5/2',
         'GPSLocation/test6/1',
         'GPSLocation/test6/2']



'''
1#pos
2#timestamp for red led start
3#red led duration
4#green led duration
'''
def getTimeStamp(timeStr):
    tm = time.strptime(timeStr, "%Y/%m/%d %H:%M:%S")
    return int(time.mktime(tm))

RGB = [((120.191689, 30.189142), getTimeStamp('2018/10/08 11:17:33'), 34, 86),
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:53:32'), 34, 86),
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 11:18:07'), 86, 34),
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:54:06'), 86, 34),
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 14:24:07'), 22, 98),
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:54:08'), 22, 98)
       ]


ConstBehavior = {1: u"正常左转",
                 2: u"正常右转",
                 3: u"正常执行",
                 4: u"违章左转",
                 5: u"违章右转",
                 6: u"违章直行",
                 7: u"掉头"}


class gaojia(object):
    xia = 0
    shang = 1
    notknow = 2

    @classmethod
    def isOK(cls, ret):
        if ret == cls.xia or ret == cls.shang:
            return True
        else:
            return False

ConstQuadrant = {1: u"东北方",
                 2: u"东南方",
                 3: u"西南方",
                 4: u"西北方"}

class dataType(object):
    xingwei = 0
    gaojia = 1
    display = 2
