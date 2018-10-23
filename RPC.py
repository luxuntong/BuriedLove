from singleton import singleton
from mqtt import MQTT


@singleton
class RPC(object):
    def __init__(self):
        pass

    def parseCmd(self, jsonData):
        cmd = jsonData['cmd']
        if hasattr(self, cmd):
            getattr(self, cmd)(jsonData)

    def test(self, jsonData):
        print(jsonData)

    def genHtml(self, jsonData):
        MQTT().generateHtml()
