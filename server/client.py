"""Client handler"""
import logging
import msgpack

from . import game

log = logging.getLogger(__name__)


class Client(object):
    def __init__(self, websocket):
        super(Client, self).__init__()
        self.ws = websocket
        self.player = self._auth()

    def _auth(self):
        game.instance.players[0].client = self
        return game.instance.players[0]

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
        data.update(game.instance.world.get_geometry())
        await self.send(data)

    async def do_tilemap(self, _):
        data = {
            'name': 'tilemap',
            'tilemap': game.instance.world.get_tiles()
        }
        await self.send(data)

    async def do_regionmap(self, _):
        data = {
            'name': 'regionmap',
            'regionmap': game.instance.world.get_regions()
        }
        await self.send(data)

    async def do_territoryborder(self, _):
        data = {
            'name': 'territoryborder',
            'bordermesh': game.instance.world.get_territory_border_mesh(0)
        }
        await self.send(data)

    async def do_revealedtiles(self, _):
        data = {
            'name': 'revealedtiles',
            'tileids': self.player.revealed_tiles()
        }
        await self.send(data)

    async def do_revealtile(self, cmd):
        self.player.reveal_tile(cmd['index'])

    async def notify_reveal_tile(self, index, reveal):
        await self.send({
            'name': 'revealtile',
            'index': index,
            'revealed': reveal
        })

    def close(self):
        game.instance.players[0].client = None
        self.ws.close()
