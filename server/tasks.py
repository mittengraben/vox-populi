"""Tasks to schedule"""
import logging


log = logging.getLogger(__name__)


class HideTileTask(object):
    def __init__(self, world, player_id, tile_index, after):
        self.player_id = player_id
        self.tile_index = tile_index
        self.after = after
        self.world = world

    async def run(self, client):
        self.world.hide_tile(self.tile_index)
        log.info('Hiding tile {}'.format(self.tile_index))
        if client:
            log.info('Notifying client')
            await client.send({
                'name': 'revealtile',
                'index': self.tile_index,
                'revealed': False
            })
