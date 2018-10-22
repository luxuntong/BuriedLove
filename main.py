# coding=utf-8
import asyncio
import threading
from mqClient import py
from mqtt import MQTT

from aiohttp import web
from aiohttp import web_runner

async def init(loop):
    app = web.Application(loop=loop)
    app = web_runner.AppRunner(app=app).app()
    app.router.add_post('/cmd/', cmd, name='cmd', expect_handler=web.Request.json)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)
    print('Server started at http://127.0.0.1:8000...')
    return srv

        
async def cmd(request):
    data = await request.json()
    print(data)
    print(MQTT().GPSPools)
    if 'name' not in data:
        return web.json_response({'error': '"name" is a required field'})

    
def start():
    loop = asyncio.get_event_loop()
    tasks = [init(loop)]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()

if __name__ == '__main__':
    t = threading.Thread(target=py.client_loop, args=('hh',))
    t.start()    
    start()