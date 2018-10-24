# coding = utf-8
import paho.mqtt.client as mqtt
from mqtt import MQTT
import time
import json
import dataset

HOST = "iotdevrd.chinacloudapp.cn"
PORT = 1889

def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class Mosquito(object) :
    def __init__(self):
        self._topic = ['GPSLocation/test1/1',
                       'GPSLocation/test1/2',
                       'GPSLocation/test2/1',
                       'GPSLocation/test2/2',
                       'GPSLocation/test3/1',
                       'GPSLocation/test3/2',
                       'GPSLocation/test4/1',
                       'GPSLocation/test4/2',
                       'GPSLocation/test5/1',
                       'GPSLocation/test5/2',
                       'GPSLocation/test6/1',
                       'GPSLocation/test6/2']
        self._current_topic_index = 0
        client_id = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        self._client = mqtt.Client(client_id)
        self._client.username_pw_set("hziottest", "123456789")
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.connect(HOST, PORT, 60)
        self._db = dataset.connect('sqlite:///gps.db')

        self._set = set()
        self._last_size = 0

    def client_loop(self, *args):
        self._client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        client.subscribe(self._get_current_topic())

    def on_message(self, client, userdata, msg):
        jData = msg.payload.decode('utf-8')
        print(msg.topic + " " + jData)
        self.save_to_sqlite(jData)
        # MQTT().setInfo(jData)

    def _get_current_topic(self):
        return self._topic[self._current_topic_index % len(self._topic)]

    def command_switch(self):
        self._client.unsubscribe(self._get_current_topic())
        self._current_topic_index += 1
        self._client.subscribe(self._get_current_topic())
        self._set = set()
        self._last_size = 0

    def save_to_sqlite(self, d):
        self._set.add(d)
        if len(self._set) == self._last_size :
            print("ok i am gonna save item")
            self._table = self._db[self._get_current_topic()]
            for gpsStr in self._set:
                self._table.insert(json.loads(gpsStr))
            self._db.commit()
            self._client.disconnect()
        else:
            self._last_size += 1
