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
        self.initUI()

    def initBrowser(self):
        view = QWebEngineView()
        channel = QWebChannel()
        handler = CallHandler()
        channel.registerObject('pyjs', handler)
        view.page().setWebChannel(channel)
        url_string = "file:///demo.html"
        view.load(QUrl(url_string))
        view.show()
        self.view = view
        self.channel = channel
        self.handler = handler

    def test(self):
        print('im in browser test')

    def createComBox(self):
        # combox
        combo = QComboBox(self)
        for text in CONST.topic:
            combo.addItem(text)
        def abc(slot):
            print('abc2 1231444')
        combo.activated[str].connect(abc)
        return combo

    def createDevCombox(self):
        combo = QComboBox(self)
        self.devComb = combo
        return combo

    def createButton(self, name):
        btn = QPushButton(name, self)
        btn.resize(btn.sizeHint())

        def abc():
            self.view.page().runJavaScript(JS_CODE.test2)
        btn.clicked.connect(abc)
        return btn

    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        self.initBrowser()
        grid.addWidget(self.createComBox(), 1, 0)
        grid.addWidget(self.createButton('Subscribe'), 1, 1)
        grid.addWidget(self.createDevCombox(), 1, 2)
        grid.addWidget(self.view, 2, 0, 2, 4)
        self.setLayout(grid)
        self.setGeometry(0, 0, 1024, 768)
        # self.showMinimized()
        self.setWindowTitle('BuriedLove')
        self.show()

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
