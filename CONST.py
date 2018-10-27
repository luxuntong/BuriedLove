# -*- coding:utf-8 -*-
import time
topic1 = ['GPSLocation/test1/1',
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
         'GPSLocation/test6/2',
         'GPSLocation/test7/1',
         'GPSLocation/test7/2',
         'GPSLocation/test8']

topic = ['GPSLocation/1',
         'GPSLocation/2',
         'GPSLocation/3',
         'GPSLocation/4',
         'GPSLocation/5',
         'GPSLocation/6',
         'GPSLocation/7',
         'GPSLocation/8',
         'GPSLocation/9',
         'GPSLocation/10']




'''
1#pos
2#timestamp for red led start
3#red led duration
4#green led duration
'''
def getTimeStamp(timeStr):
    tm = time.strptime(timeStr, "%Y/%m/%d %H:%M:%S")
    return int(time.mktime(tm))

RGB = [((120.191689, 30.189142), getTimeStamp('2018/10/08 11:17:33'), 34, 86),#0
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:53:32'), 34, 86),#1
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 11:18:07'), 86, 34),#2
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:54:06'), 86, 34),#3
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 14:24:07'), 22, 98),#4
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:54:08'), 22, 98),#5
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 11:17:33'), 34, 86),#6
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:53:32'), 34, 86),#7
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 14:24:29'), 98, 22),#8
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:54:30'), 98, 22),#9
       ((120.191689, 30.189142), getTimeStamp('2018/10/08 11:17:33'), 34, 86),#10
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:53:32'), 34, 86),#11
       ((120.191689, 30.189142), getTimeStamp('2018/10/09 10:54:08'), 22, 98)#12
       ]

class DIR(object):
    left = 0
    forward = 1
    right = 2

class BHType(object):
    lvzhi = 0
    lvyou = 1
    lvzuo = 2
    hongzhi = 3
    hongyou = 4
    hongzuo = 5
    hongdeng = 6


ConstBehavior = {1: u"绿灯左转",
                 2: u"绿灯右转",
                 3: u"绿灯直行",
                 4: u"红灯左转",
                 5: u"红灯右转",
                 6: u"红灯直行",
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
