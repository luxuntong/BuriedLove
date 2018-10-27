# -*- coding:utf-8 -*-
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
         'GPSLocation/test6/2',
         'GPSLocation/test7/1',
         'GPSLocation/test7/2',
         'GPSLocation/test8']



'''
1#pos
2#timestamp for red led start
3#red led duration
4#green led duration
'''
RGB = [((120.191689, 30.189142), 1538982539, 40, 20),
       ((120.18871666666668, 30.185471666666665), 1539051068, 20, 20)]


ConstBehavior = {1: u"正常左转",
                 2: u"正常右转",
                 3: u"正常执行",
                 4: u"非法左转",
                 5: u"非法右转",
                 6: u"非法直行",
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
