"""World object"""
import logging
import random

from .hexsphere import Edge
from .hexsphere import HexSphere


log = logging.getLogger(__name__)


class WorldTile(object):
    __slots__ = ['index', 'geometry', 'region', '_neighbours']

    def __init__(self, index, geometry):
        super(WorldTile, self).__init__()
        self.index = index
        self.geometry = geometry
        geometry.world = self
        self.region = None

        self._neighbours = None

    def neighbours(self):
        if self._neighbours is None:
            self._neighbours = [
                e.neighbour.tile.world for e in self.geometry.edges
            ]
        return self._neighbours


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


class World(object):
    def __init__(self, config):
        subdivisions = config.get('world_subdiv', 4)

        self.sphere = HexSphere(subdiv=subdivisions)
        self.geometry = self.sphere.emit()
        log.info('Generating world...')

        self.tiles = [WorldTile(i, x) for i, x in self.sphere.tiles.items()]

        self.regions = []
        self._generate_regions(count=config.get('world_regions', 85))

        log.info('World generated')
        log.info('Subdivisions {}'.format(subdivisions))
        log.info('Vertices {}'.format(len(self.geometry['position']) // 3))
        log.info('Tiles {}'.format(len(self.tiles)))
        log.info('Regions {}'.format(len(self.regions)))

    def _generate_regions(self, count):
        self.regions = [WorldRegion(i) for i in range(count)]
        seeds = random.sample(self.tiles, count)

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
