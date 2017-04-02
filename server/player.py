from . import game
from .territory import Territory


class Player(object):
    def __init__(self, index):
        self.index = index
        self.territory = Territory(game.instance.world.regions[13])
        self.client = None

    def reveal_tile(self, index):
        tile = game.instance.world.tile_map[index]
        if not self.territory.has_region(tile.region):
            return

        tile.reveal(self)

    def revealed_tiles(self):
        return [
            x.index for x in game.instance.world.tile_map if x.visible(self)
        ]
