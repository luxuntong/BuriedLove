# coding = utf-8
import paho.mqtt.client as mqtt
from mqtt import MQTT
import time
import json
# import dataset
import CONST
#TODO
HOST = "iotdevrd.chinacloudapp.cn"
PORT = 1889
user = 'hziottest'
pwd = '123456789'

'''
HOST = '3.1.2.244'
PORT = 1889
user = 'iotadmin'
pwd = 'iotadmin_2018'
'''


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*argss):
        if cls not in instances:
            instances[cls] = cls(*argss, **kw)
        return instances[cls]
    return _singleton


g_mqtt = MQTT()


@singleton
class Mosquito(object):
    def __init__(self, browser):
        client_id = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self._client = mqtt.Client(client_id)
        #self._client.username_pw_set("hziottest", "123456789")
        self._client.username_pw_set(user, pwd)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.connect(HOST, PORT, 60)
        # self._db = dataset.connect('sqlite:///gps.db')
        self._browser = browser
        g_mqtt.setBrowser(browser, self)
        self._topic = ''
        self._last_topic = ''

        self._set = set()
        self._last_size = 0

        self.client_loop()

    def client_loop(self, *args):
        self._client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # client.subscribe(self._get_current_topic())

    def on_message(self, client, userdata, msg):
        jData = msg.payload.decode('utf-8')
        print(msg.topic + " " + jData)
        # self.save_to_sqlite(jData)
        g_mqtt.setInfo(msg.topic, jData)

    def _get_current_topic(self):
        # return CONST.topic[self._current_topic_index % len(CONST.topic)]
        return self._topic

    def set_current_topic(self, topic):
        print('set topic:', topic)
        self._last_topic = self._topic
        self._topic = topic

    def command_switch(self):
        if self._last_topic:
            self._client.unsubscribe(self._last_topic)
        self._client.subscribe(self._get_current_topic())
        self._set = set()
        self._last_size = 0

    def save_to_sqlite(self, d):
        self._set.add(d)
        if len(self._set) == self._last_size:
            print("ok i am gonna save item")
            self._table = self._db[self._get_current_topic()]
            for gpsStr in self._set:
                self._table.insert(json.loads(gpsStr))
            self._db.commit()
            self._client.disconnect()
        else:
            self._last_size += 1
