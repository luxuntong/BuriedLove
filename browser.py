#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
# from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QComboBox, QScrollArea,
                             QCheckBox, QLabel, QVBoxLayout, QApplication)
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
# from PyQt5.QtCore import *
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from display import Ana
import recog
from PyQt5.QtGui import QFont
import JS_CODE
import CONST



class CallHandler(QObject):
    def __init__(self, browser):
        super(CallHandler, self).__init__()
        self._browser = browser

    @pyqtSlot(result=str)
    def init(self):
        print('im in browser init')
        self._browser.initFocus()
        return 'browser'

    @pyqtSlot(result=str)
    def myHello(self):
        print('im in hello')
        # view.page().runJavaScript('uptext("hello, Python");')
        print('call received')
        return 'hello, Python'

    @pyqtSlot(str, result=str)
    def myTest(self, test):
        return test


class Browser(QWidget):

    def __init__(self):
        super().__init__()
        self._mqtt = None
        self._topics = {}
        self._topic = CONST.topic[0]
        self._devId = ''
        self._poss = {}
        pos = CONST.RGB[0][0]
        pos = recog.getCorrectedCord(*pos)
        self._posStr = str(pos)
        self.initUI()
        self._downloadMod = True
        self._downloadIndex = 6
        self._registerInfo = None


    def initBrowser(self):
        view = QWebEngineView()
        channel = QWebChannel()
        handler = CallHandler(self)
        channel.registerObject('pyjs', handler)
        view.page().setWebChannel(channel)
        url_string = "file:///html/demo.html"
        view.load(QUrl(url_string))
        view.show()
        self.view = view
        self.channel = channel
        self.handler = handler

    def initFocus(self):
        self.setPos(self._posStr)

    def test(self):
        print('im in browser test')

    def createComBox(self):
        # combox
        combo = QComboBox(self)
        for text in CONST.topic:
            combo.addItem(text)

        def changeTopic(slot):
            self._topic = slot

        combo.activated[str].connect(changeTopic)
        return combo

    def createDevCombox(self):
        combo = QComboBox(self)
        self.devComb = combo

        def changeDevId(devId):
            self._devId = devId

        combo.activated[str].connect(changeDevId)
        return combo

    def subScribe(self):
        if not self._mqtt:
            print('ERROR: mqtt not set')
            return

        self._mqtt.doMosFunc('set_current_topic', (self._topic, ))
        self._mqtt.doMosFunc('command_switch', ())
        self.devComb.clear()

    def setPos(self, posStr):
        self._posStr = posStr
        jsStr = JS_CODE.focus.replace('ckzlt_pos', posStr)
        print(jsStr)
        self.view.page().runJavaScript(jsStr)

    def createPosCombox(self):
        combo = QComboBox(self)
        for posInfo in CONST.RGB:
            posStr = str(posInfo[0])
            combo.addItem(posStr)
            self._poss[posStr] = posInfo

        combo.activated[str].connect(self.setPos)
        return combo

    def createButton(self, name, func):
        btn = QPushButton(name, self)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(func)
        return btn

    def onGetPointsData(self, points):
        print('getData:', len(points), points)
        self.view.page().runJavaScript(JS_CODE.removeOverlay)
        points = [recog.getCorrectedCord(gps.longitude, gps.latitude) for gps in points]
        points = ['new BMap.Point({},{})'.format(pos[0], pos[1]) for pos in points]
        pointsStr = ',\n\t'.join(points)
        jsStr = JS_CODE.addOverlay.replace('ckzlt_points', pointsStr)
        self.view.page().runJavaScript(jsStr)

    def register(self):
        print('register:', self._devId)
        self._mqtt.register(self._topic, self._devId, 'browser', self.onGetPointsData)
        self._registerInfo = (self._topic, self._devId)
        
    def createScroll(self):
        self.topFiller = QWidget()
        self.topFiller.setMinimumSize(200, 100)
        grid = QGridLayout()
        self.topFiller.setLayout(grid)
        for i in range(2):
            bt = QPushButton('123', self)
            grid.addWidget(bt, i, 0)
        scroll = QScrollArea()
        scroll.setWidget(self.topFiller)
        scroll.setGeometry(0, 0, 50, 50)
        scroll.setMinimumSize(50, 50)
        # scroll.resize(1, 1)
        self.devGrid = grid
        self.scroll = scroll
        return scroll

    def createStatus(self):
        lbl = QLabel(self)
        self._statusLbl = lbl
        return lbl

    def setStatus(self, data):
        self._statusLbl.setText(data)

    def createLabel(self):
        lbl = QLabel(self)
        self._logLbl = lbl
        return lbl

    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        self.initBrowser()
        grid.addWidget(self.createComBox(), 1, 0)
        grid.addWidget(self.createButton('Subscribe', self.subScribe), 1, 1)
        grid.addWidget(self.createDevCombox(), 1, 2)
        grid.addWidget(self.createButton('Register', self.register), 1, 3)
        grid.addWidget(self.createPosCombox(), 2, 0)
        grid.addWidget(self.createButton('test', self.testResult), 3, 0)
        grid.addWidget(self.createStatus(), 4, 0)
        grid.addWidget(self.createLabel(), 2, 1, 3, 3)
        grid.addWidget(self.view, 5, 0, 3, 4)
        self.setLayout(grid)
        # self.setGeometry(0, 0, 1024, 768)
        self.setGeometry(0, 0, 1024, 768)
        # self.showMinimized()
        self.setWindowTitle('BuriedLove')
        self.show()

        self.setPos(self._posStr)

    def testResult(self):
        retData = 'Result:\n'
        try:
            topicData = self._mqtt.getTopicDict(self._topic)
            index = CONST.topic.index(self._topic)
            ana = Ana(self._topic, topicData)
            dataType = CONST.getDataType(index)
            rets = ana.anaAll(dataType)
            print(rets)
            for devId, ret in rets.items():
                retData += devId + ': ' + ret + '\n'

            print(retData)
            self._logLbl.setText(retData)

        except Exception as e:
            print(e)

    def getCurrTopicInfo(self):
        strRet = 'topic:{}\n'.format(self._topic)
        devs = self._topics[self._topic]
        devs = [key + (': finished' if right else ': receiving') for key, right in devs.items()]
        devData = '\n'.join(devs)
        strRet += devData
        return strRet

    def addDevId(self, devId):
        self._topics.setdefault(self._topic, {})
        self._topics[self._topic][devId] = False
        self.devComb.addItem(devId)
        if not self._devId:
            self._devId = devId

        self.setStatus('receive')
        self._logLbl.setText(self.getCurrTopicInfo())

    def setMqtt(self, mqtt):
        self._mqtt = mqtt

    def devFull(self, devId):
        self._topics[self._topic][devId] = True
        self._logLbl.setText(self.getCurrTopicInfo())

    def mqttAllFull(self):
        self.testResult()
        self.setStatus('finished')


def browserGo():
    app = QApplication(sys.argv)
    yield Browser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    bg = browserGo()
    ex = next(bg)
    next(bg)
