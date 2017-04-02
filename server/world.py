"""World object"""
import asyncio
import logging
import random

from .hexsphere import Edge
from .hexsphere import HexSphere

from .territory import Territory
from . import game


log = logging.getLogger(__name__)


class WorldTile(object):
    __slots__ = ['index', 'geometry', 'region', '_neighbours', 'revealed_for']

    def __init__(self, index, geometry):
        super(WorldTile, self).__init__()
        self.index = index
        self.geometry = geometry
        geometry.world = self
        self.region = None
        self.revealed_for = set()

        self._neighbours = None

    def neighbours(self):
        if self._neighbours is None:
            self._neighbours = [
                e.neighbour.tile.world for e in self.geometry.edges
            ]
        return self._neighbours

    def _hide_for(self, player):
        log.info(
            'hiding tile {} for player {}'.format(self.index, player.index)
        )
        self.revealed_for.discard(player.index)
        if player.client:
            asyncio.ensure_future(
                player.client.notify_reveal_tile(self.index, False)
            )

    def reveal(self, player):
        if player.index in self.revealed_for:
            return

        log.info(
            'showing tile {} for player {}'.format(self.index, player.index)
        )
        self.revealed_for.add(player.index)
        if player.client:
            asyncio.ensure_future(
                player.client.notify_reveal_tile(self.index, True)
            )
        game.instance.schedule(
            target=self,
            action=WorldTile._hide_for,
            args=[player],
            after=5.0
        )

    def visible(self, player):
        if player.index in self.revealed_for:
            return True
        return False


class WorldRegion(object):
    def __init__(self, index):
        super(WorldRegion, self).__init__()
        self.index = index
        self.tiles = []
        self._border_cache = None

    def add_tile(self, tile):
        self.tiles.append(tile)
        tile.region = self

        self._border_cache = None

    def flood_fill(self, front):
        new_front = []
        for tile in front:
            for neighbour in tile.neighbours():
                if neighbour.region is None:
                    self.tiles.append(neighbour)
                    neighbour.region = self
                    new_front.append(neighbour)
        if new_front:
            self._border_cache = None
        return new_front

    def border(self):
        if self._border_cache is None:
            edges = []
            for tile in self.tiles:
                for edge in tile.geometry.edges:
                    if edge.neighbour.tile.world.region != self:
                        edges.append(edge)
            self._border_cache = Edge.chain_sort(edges)

        return self._border_cache

    def emit_border(self):
        return (e.p1 for e in self.border())


class World(object):
    def __init__(self, config):
        subdivisions = config.get('world_subdiv', 4)

        self.sphere = HexSphere(subdiv=subdivisions)
        self.geometry = self.sphere.emit()
        log.info('Generating world...')

        self.tile_map = [
            WorldTile(i, x) for i, x in enumerate(self.sphere.tiles)
        ]

        self._tile_cache = None

        self.regions = []
        self._region_cache = None
        self._generate_regions(count=config.get('world_regions', 85))

        self.territories = [Territory(self.regions[13])]

        log.info('World generated')
        log.info('Subdivisions {}'.format(subdivisions))
        log.info('Vertices {}'.format(len(self.geometry['position']) // 3))
        log.info('Tiles {}'.format(len(self.tile_map)))
        log.info('Regions {}'.format(len(self.regions)))

    def _generate_regions(self, count):
        self.regions = [WorldRegion(i) for i in range(count)]
        seeds = random.sample(self.tile_map, count)

        fronts = []
        for region, seed in zip(self.regions, seeds):
            region.add_tile(seed)
            fronts.append((region, [seed]))

        while fronts:
            new_fronts = []
            for region, front in fronts:
                new_front = region.flood_fill(front)
                if new_front:
                    new_fronts.append((region, new_front))
            fronts = new_fronts

        edge_set = {x for region in self.regions for x in region.border()}
        indicies = []
        for e in edge_set:
            indicies.extend((e.p1, e.p2))
        self.geometry['bordermesh'] = indicies

    def get_geometry(self):
        return self.geometry

    def get_tiles(self):
        if self._tile_cache is None:
            self._tile_cache = [
                {
                    'vertices': t.geometry.emit_vertices(),
                    'center': t.geometry.center,
                    'region': t.region.index
                }
                for t in self.tile_map
            ]
        return self._tile_cache

    def get_regions(self):
        if self._region_cache is None:
            self._region_cache = [
                {
                    'border': list(r.emit_border())
                }
                for r in self.regions
            ]
        return self._region_cache

    def get_territory_border_mesh(self, territory_id):
        return self.territories[territory_id].border_mesh()

    def get_revealed_tiles_for_territory(self, territory_id):
        return self.territories[territory_id].revealed_tiles()
