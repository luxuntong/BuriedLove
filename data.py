import dataset
import time
import json
from singleton import singleton


@singleton
class Data(object):
    def __init__(self):
        print('data init:', id(self))
        self._db = dataset.connect('sqlite:///gps_ckz.db')
        self._table = self._db['gps1']
        self._count = 0

    def addData(self, jsonStr):
        self._count += 1
        self._table.insert({'data': jsonStr})

        if self._count == 10:
            self._count = 0
            self._db.commit()

    def getDatas(self):
        for data in self._table.find():
            yield data

    def test(self):
        # self._table.insert({'a': 123, 'b': 333})
        print('im in test1')
        for i in range(100):
            self.addData(str(i))
        print('im in test')
        for data in self.getDatas():
            print(data)

        1538982539
        ret = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1538982539))
        print(ret)


if __name__ == '__main__':
    Data().test()
