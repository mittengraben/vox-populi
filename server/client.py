"""Client handler"""
import logging
import msgpack

log = logging.getLogger(__name__)


class Client(object):
    def __init__(self, websocket, world):
        super(Client, self).__init__()
        self.ws = websocket
        self.world = world

    async def recv(self):
        return msgpack.unpackb(
            await self.ws.recv(), encoding='utf-8'
        )

    async def send(self, data):
        await self.ws.send(msgpack.packb(data))

    async def run(self):
        try:
            while True:
                command = await self.recv()
                if hasattr(self, 'do_' + command['name']):
                    await getattr(self, 'do_' + command['name'])(command)
        except Exception as exc:
            log.error('{}: {}'.format(type(exc), exc))

    async def do_hello(self, _):
        await self.send({'name': 'hello', 'response': 'hi'})

    async def do_worldgeometry(self, _):
        data = {
            'name': 'worldgeometry'
        }
        data.update(self.world.get_geometry())
        await self.send(data)

    def close(self):
        self.ws.close()
