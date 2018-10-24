#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView

class CallHandler(QObject):
    @pyqtSlot(result = str)
    def myHello(self):
        view.page().runJavaScript('uptext("hello, Python");')
        print('call received')
        return 'hello, Python'
    
    @pyqtSlot(str,result=str)
    def myTest(self,test):
        return test

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QWebEngineView()
    channel = QWebChannel()
    handler = CallHandler()
    channel.registerObject('pyjs', handler)
    view.page().setWebChannel(channel)
    url_string = "file:///qtest.html"
    view.load(QUrl(url_string))
    view.show()
    sys.exit(app.exec_())