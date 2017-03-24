import itertools

from .hexsphere import _Point
from .hexsphere import Edge
from .hexsphere import Tile


class Territory(object):
    def __init__(self, region):
        super(Territory, self).__init__()
        self.regions = [region]
        self._region_set = {x.index for x in self.regions}
        self._border_mesh_cache = None

    def border_mesh(self):
        if self._border_mesh_cache is None:
            border_loop = Edge.chain_sort(
                list((
                    e for e in
                    itertools.chain(*(x.border() for x in self.regions))
                    if (
                        e.neighbour.tile.world.region.index not in
                        self._region_set or
                        e.tile.world.region.index
                        not in self._region_set
                    )
                ))
            )
            border_points = [_Point.from_index(x.p2) for x in border_loop]
            border_loop.append(border_loop[0])
            displaced_points = []
            for index in range(len(border_points)):
                point = border_points[index]
                tile = border_loop[index].tile
                next_tile = border_loop[index + 1].tile

                towards = tile.center
                if tile != next_tile:
                    towards = Tile.shared_edge(
                        tile, next_tile
                    ).other_point(point.index)
                displaced_points.append(_Point.move(
                    point, _Point.from_index(towards), 0.3
                ))

            pointlist = list(range((len(border_points) + 1) * 2))
            pointlist[-2] = 0
            pointlist[-1] = 1
            points = border_points + displaced_points
            points[::2] = border_points
            points[1::2] = displaced_points
            vertices = []
            for point in points:
                vertices.extend([point.x, point.y, point.z])

            self._border_mesh_cache = {
                'position': vertices,
                'indicies': pointlist
            }
        return self._border_mesh_cache
