# coding=utf-8
import asyncio
import threading
from mqClient import py
from RPC import RPC
import dataset
from mqtt import MQTT
from browser import browserGo
import json

from aiohttp import web
from aiohttp import web_runner


DBNAME = 'sqlite:///gps.db'


async def init(loop):
    app = web.Application(loop=loop)
    app = web_runner.AppRunner(app=app).app()
    app.router.add_post('/cmd/', cmd, name='cmd',
                        expect_handler=web.Request.json)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server started at http://127.0.0.1:8000...')
    return srv


async def cmd(request):
    data = await request.json()
    RPC().parseCmd(data)
    return web.json_response({'result': 'success'})


def start():
    loop = asyncio.get_event_loop()
    tasks = [init(loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()


def startMos(browser):
    mos = py.Mosquito(browser)


if __name__ == '__main__':
    bg = browserGo()
    browser = next(bg)
    mos = py.Mosquito(browser)
    # startMos(browser)
    next(bg)
'''
    db = dataset.connect(DBNAME)
    for gpsDict in db['GPSLocation/test1/1'].all():
        gpsStr = json.dumps(gpsDict)
        print(type(gpsStr), gpsStr)
        MQTT().setInfo(gpsStr)
'''
