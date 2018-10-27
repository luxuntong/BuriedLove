import time
aa = set()
aa.add(1)
aa.add(2)
bb = {}
bb['a'] = 99
bb['c'] = 33
bb['b'] = 77
print(len(aa))
print(len(bb))

tm = time.strptime("2018/10/08 11:17:33","%Y/%m/%d %H:%M:%S")
print(tm)
print(time.mktime(tm))