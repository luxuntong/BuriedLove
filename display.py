import matplotlib.pyplot as plt
import random
from mqtt import GPSPool
from matplotlib import colors as mcolors
import os

colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                for name, color in colors.items())
sorted_names = [name for hsv, name in by_hsv]
class Ana(object):
    def __init__(self):
        files = os.listdir('data')
        self.GPSPools = {}
        for name in files:
            self.GPSPools[name] = self.createGP(name)
        
    def createGP(self, filename):
        gp = GPSPool('1', filename, None)
        with open('data\\' + filename) as fr:
            for line in fr:
                gp.addData(line)
        return gp
    
    def getData(self, devId):
        return self.GPSPools[devId].getSortData()
    
    def getAllData(self):
        for gp in self.GPSPools.values():
            yield gp.getSortData()
    
    def test(self):
        print(len(self.gp.getSortData()))
        
if __name__ == '__main__':
    ana = Ana()
    fig = plt.figure(1, facecolor='white')
    fig.clf()
    axl = plt.subplot(111, frameon=False)
    for index, data in enumerate(ana.getAllData()):        
        x = [gps.timestamp for gps in data]
        y = [gps.speed for gps in data]
        plt.plot(x, y, color=colors[sorted_names[index]])
    plt.show()