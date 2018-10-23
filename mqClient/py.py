# coding = utf-8
import paho.mqtt.client as mqtt
from mqtt import MQTT
import time

HOST = "iotdevrd.chinacloudapp.cn"
PORT = 1889


def client_loop(*args):
    client_id = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    client = mqtt.Client(client_id)
    client.username_pw_set("hziottest", "123456789")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, 60)
    client.loop_forever()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("GPSLocation/test1/1")


def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))
    MQTT().setInfo(msg.payload.decode("utf-8"))


if __name__ == '__main__':
    client_loop()
