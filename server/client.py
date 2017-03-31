"""Client handler"""
import logging
import msgpack

from . import tasks


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
        except Exception:
            log.exception('during command execution')

    async def do_hello(self, _):
        await self.send({'name': 'hello', 'response': 'hi'})

    async def do_worldgeometry(self, _):
        data = {
            'name': 'worldgeometry'
        }
        data.update(self.world.get_geometry())
        await self.send(data)

    async def do_tilemap(self, _):
        data = {
            'name': 'tilemap',
            'tilemap': self.world.get_tiles()
        }
        await self.send(data)

    async def do_regionmap(self, _):
        data = {
            'name': 'regionmap',
            'regionmap': self.world.get_regions()
        }
        await self.send(data)

    async def do_territoryborder(self, _):
        data = {
            'name': 'territoryborder',
            'bordermesh': self.world.get_territory_border_mesh(0)
        }
        await self.send(data)

    async def do_revealedtiles(self, _):
        data = {
            'name': 'revealedtiles',
            'tileids': self.world.get_revealed_tiles_for_territory(0)
        }
        await self.send(data)

    async def do_revealtile(self, cmd):
        if self.world.reveal_tile(cmd['index'], territory_id=0):
            self.world.timers.schedule(
                tasks.HideTileTask(
                    world=self.world,
                    player_id=0,
                    tile_index=cmd['index'],
                    after=5.0
                )
            )
            await self.send({
                'name': 'revealtile',
                'index': cmd['index'],
                'revealed': True
            })

    def close(self):
        self.ws.close()
