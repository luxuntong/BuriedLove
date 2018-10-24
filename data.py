import dataset
from singleton import singleton


@singleton
class Data(object):
    def __init__(self):
        self._db = dataset.connect('sqlite:///gps.db')
        self._table = self._db['test']
        
    def addData(self, jsonStr):
        self._table.insert({'data': jsonStr})
        
    def getDatas(self):
        for data in self._table.find():
            yield data
        
    def test(self):
        # self._table.insert({'a': 123, 'b': 333})
        for data in self.getDatas():
            print(data)
        
if __name__ == '__main__':
    Data().test()
        
        