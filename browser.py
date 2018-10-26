#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
# from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import (QWidget, QPushButton, QGridLayout, QComboBox,
                             QLabel, QVBoxLayout, QApplication)
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
# from PyQt5.QtCore import *
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
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
        self._posStr = str(CONST.RGB[0][0])
        self.initUI()

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

    def setPos(self, posStr):
        self._posStr = posStr
        jsStr = JS_CODE.focus.replace('ckzlt_pos', posStr)
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
        print('getData:', points)
        self.view.page().runJavaScript(JS_CODE.removeOverlay)
        points = ['new BMap.Point({},{})'.format(gps.longitude, gps.latitude) for gps in points]
        pointsStr = ',\n\t'.join(points)
        jsStr = JS_CODE.addOverlay.replace('ckzlt_points', pointsStr)
        self.view.page().runJavaScript(jsStr)

    def register(self):
        print('register:', self._devId)
        self._mqtt.register(self._devId, 'browser', self.onGetPointsData)

    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        self.initBrowser()
        grid.addWidget(self.createComBox(), 1, 0)
        grid.addWidget(self.createButton('Subscribe', self.subScribe), 1, 1)
        grid.addWidget(self.createDevCombox(), 1, 2)
        grid.addWidget(self.createButton('Register', self.register), 1, 3)
        grid.addWidget(self.createPosCombox(), 2, 0)
        grid.addWidget(self.view, 3, 0, 3, 4)
        self.setLayout(grid)
        # self.setGeometry(0, 0, 1024, 768)
        self.setGeometry(1000, 600, 300, 300)
        # self.showMinimized()
        self.setWindowTitle('BuriedLove')
        self.show()

        self.setPos(self._posStr)

    def addDevId(self, devId):
        self._topics.setdefault(self._topic, [])
        self._topics[self._topic].append(devId)
        self.devComb.addItem(devId)
        if not self._devId:
            self._devId = devId

    def setMqtt(self, mqtt):
        self._mqtt = mqtt


def browserGo():
    app = QApplication(sys.argv)
    yield Browser()
    sys.exit(app.exec_())


if __name__ == '__main__':
    bg = browserGo()
    ex = next(bg)
    next(bg)
