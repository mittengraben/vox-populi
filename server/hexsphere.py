"""Hexsphere generator"""
import math


def _normalize(x, y, z):
    magnitude = math.sqrt(
        x * x +
        y * y +
        z * z
    )
    return (
        x / magnitude,
        y / magnitude,
        z / magnitude
    )


class Vector3(object):
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x, y, z):
        super(Vector3, self).__init__()
        self.x, self.y, self.z = x, y, z

    def magnitude(self):
        return math.sqrt(
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )

    def normalize(self):
        mag = self.magnitude()
        self.x /= mag
        self.y /= mag
        self.z /= mag

    def mul(self, scalar):
        return Vector3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar
        )

    @classmethod
    def from_ab(cls, a, b):
        return cls(
            b.x - a.x,
            b.y - a.y,
            b.z - a.z
        )

    def add_to(self, p):
        return Vector3(
            p.x + self.x,
            p.y + self.y,
            p.z + self.z
        )


class _Point(object):
    __slots__ = ['x', 'y', 'z', 'index']

    _container = []
    _midpoints = {}

    def __init__(self, x, y, z):
        super(_Point, self).__init__()
        self.x, self.y, self.z = x, y, z
        self.index = len(_Point._container)
        _Point._container.append(self)

    @classmethod
    def from_index(cls, index):
        return cls._container[index]

    @classmethod
    def move(cls, point, towards, delta):
        vec = Vector3.from_ab(point, towards)
        vec = vec.mul(delta).add_to(point)

        return vec

    def __repr__(self):
        return '<Point {}>'.format(
            self.index, self.x, self.y, self.z
        )

    def reproject(self):  # i.e. normalize
        self.x, self.y, self.z = _normalize(self.x, self.y, self.z)

    @staticmethod
    def sphere_midpoint(p1, p2):
        key = tuple(sorted([p1, p2]))
        p1 = _Point.from_index(p1)
        p2 = _Point.from_index(p2)
        if key in _Point._midpoints:
            return _Point._midpoints[key]
        flat_midpoint = _Point(
            ((p2.x - p1.x) * 0.5 + p1.x),
            ((p2.y - p1.y) * 0.5 + p1.y),
            ((p2.z - p1.z) * 0.5 + p1.z),
        )
        flat_midpoint.reproject()
        _Point._midpoints[key] = flat_midpoint.index
        return flat_midpoint.index


class _Face(object):
    __slots__ = ['v1', 'v2', 'v3', 'centroid']

    def __init__(self, v1, v2, v3):
        super(_Face, self).__init__()
        self.v1, self.v2, self.v3 = v1, v2, v3
        self._find_centroid()

    def __repr__(self):
        return '<Face {}/{}/{}>'.format(
            repr(self.v1), repr(self.v2), repr(self.v3)
        )

    def subdivide(self):
        p12 = _Point.sphere_midpoint(self.v1, self.v2)
        p23 = _Point.sphere_midpoint(self.v2, self.v3)
        p31 = _Point.sphere_midpoint(self.v1, self.v3)

        f1 = _Face(self.v1, p12, p31)
        f2 = _Face(p12, p23, p31)
        f3 = _Face(p31, p23, self.v3)
        f4 = _Face(p12, self.v2, p23)

        return (f1, f2, f3, f4)

    def _find_centroid(self):
        v1 = _Point.from_index(self.v1)
        v2 = _Point.from_index(self.v2)
        v3 = _Point.from_index(self.v3)
        centroid = _Point(
            (v1.x + v2.x + v3.x) / 3.0,
            (v1.y + v2.y + v3.y) / 3.0,
            (v1.z + v2.z + v3.z) / 3.0
        )
        centroid.reproject()
        self.centroid = centroid.index

    def is_fa(self, p1, p2):
        slist = [self.v1, self.v2, self.v3, self.v1]
        for i in range(len(slist)):
            if p1 == slist[i]:
                break
        return p2 == slist[i+1]

    def shared_edge(self, other):
        self_set = set([self.v1, self.v2, self.v3])
        other_set = set([other.v1, other.v2, other.v3])

        common = self_set & other_set
        if len(common) != 2:
            return None

        return common

    def bucket_keys(self):
        indicies = sorted([self.v1, self.v2, self.v3])
        return (
            (indicies[0], indicies[1]),
            (indicies[1], indicies[2]),
            (indicies[0], indicies[2])
        )


class Edge(object):
    __slots__ = ['p1', 'p2', 'neighbour', 'tile', '_hash']
    _container = {}

    def __init__(self, p1, p2):
        super(Edge, self).__init__()
        self.p1 = p1
        self.p2 = p2
        self.tile = None
        self.neighbour = None

        key = tuple(sorted([p1, p2]))
        self._hash = hash(key)

        Edge._container.setdefault(key, self)

    def other_point(self, p):
        if self.p1 == p:
            return self.p2
        else:
            return self.p1

    @staticmethod
    def neighbours(e1, e2):
        e1.neighbour, e2.neighbour = e2, e1

    @staticmethod
    def chain_sort(edges):
        p1_dict = {e.p1: e for e in edges}

        start_point = edges[0].p1
        next_point = edges[0].p2
        sorted_edges = [edges[0]]

        while next_point != start_point:
            edge = p1_dict[next_point]
            sorted_edges.append(edge)
            next_point = edge.p2
        return sorted_edges


class Tile(object):
    __slots__ = ['edges', 'center', 'world']

    def __init__(self):
        super(Tile, self).__init__()
        self.center = None
        self.edges = []
        self.world = None

    def add_edge(self, edge):
        edge.tile = self
        self.edges.append(edge)

    def postprocess(self):
        self.edges = Edge.chain_sort(self.edges)

        x, y, z = 0, 0, 0
        for e in self.edges:
            pt = _Point.from_index(e.p1)
            x += pt.x
            y += pt.y
            z += pt.z

        count = len(self.edges)
        center = _Point.from_index(self.center)
        center.x = x / count
        center.y = y / count
        center.z = z / count

    def emit_faces(self):
        vertices = self.emit_vertices()
        vertices.append(vertices[0])
        faces = []
        for index in range(len(self.edges)):
            faces.append(self.center)
            faces.append(vertices[index + 1])
            faces.append(vertices[index])
        return faces

    def emit_vertices(self):
        return [e.p1 for e in self.edges]

    @staticmethod
    def shared_edge(t1, t2):
        for e in t1.edges:
            if e.neighbour.tile == t2:
                return e
        return None


def icosahedron():
    PHI = (1.0 + math.sqrt(5.0)) / 2.0
    DU = 1.0 / math.sqrt(PHI * PHI + 1.0)
    DV = PHI * DU

    VERTICES = [
        _Point(0, +DV, +DU).index,
        _Point(0, +DV, -DU).index,
        _Point(0, -DV, +DU).index,
        _Point(0, -DV, -DU).index,
        _Point(+DU, 0, +DV).index,
        _Point(-DU, 0, +DV).index,
        _Point(+DU, 0, -DV).index,
        _Point(-DU, 0, -DV).index,
        _Point(+DV, +DU, 0).index,
        _Point(+DV, -DU, 0).index,
        _Point(-DV, +DU, 0).index,
        _Point(-DV, -DU, 0).index,
    ]

    FACES = [
        _Face(VERTICES[0], VERTICES[1], VERTICES[8]),
        _Face(VERTICES[0], VERTICES[4], VERTICES[5]),
        _Face(VERTICES[0], VERTICES[5], VERTICES[10]),
        _Face(VERTICES[0], VERTICES[8], VERTICES[4]),
        _Face(VERTICES[0], VERTICES[10], VERTICES[1]),
        _Face(VERTICES[1], VERTICES[6], VERTICES[8]),
        _Face(VERTICES[1], VERTICES[7], VERTICES[6]),
        _Face(VERTICES[1], VERTICES[10], VERTICES[7]),
        _Face(VERTICES[2], VERTICES[3], VERTICES[11]),
        _Face(VERTICES[2], VERTICES[4], VERTICES[9]),
        _Face(VERTICES[2], VERTICES[5], VERTICES[4]),
        _Face(VERTICES[2], VERTICES[9], VERTICES[3]),
        _Face(VERTICES[2], VERTICES[11], VERTICES[5]),
        _Face(VERTICES[3], VERTICES[6], VERTICES[7]),
        _Face(VERTICES[3], VERTICES[7], VERTICES[11]),
        _Face(VERTICES[3], VERTICES[9], VERTICES[6]),
        _Face(VERTICES[4], VERTICES[8], VERTICES[9]),
        _Face(VERTICES[5], VERTICES[11], VERTICES[10]),
        _Face(VERTICES[6], VERTICES[9], VERTICES[8]),
        _Face(VERTICES[7], VERTICES[10], VERTICES[11])
    ]
    return FACES


class HexSphere(object):
    def __init__(self, subdiv):
        self.faces = icosahedron()
        self.tiles = {}
        for _ in range(subdiv):
            self._subdivide()
        self._make_dual()

    def _subdivide(self):
        new_faces = []

        for face in self.faces:
            new_faces.extend(face.subdivide())

        self.faces = new_faces

    def _make_face_pairs(self):
        face_buckets = {}
        for face in self.faces:
            for k in face.bucket_keys():
                face_buckets.setdefault(k, []).append(face)

        for face_list in face_buckets.values():
            if len(face_list) == 2:
                f1, f2 = face_list
                shared = f1.shared_edge(f2)
                if shared is not None:
                    p1, p2 = shared
                    if f1.is_fa(p1, p2):
                        yield (p1, p2, f1, f2)
                    else:
                        yield (p1, p2, f2, f1)
                else:
                    raise RuntimeError('Not exactly')

    def _make_dual(self):
        for p1, p2, fa, fb in self._make_face_pairs():
            ac = fa.centroid
            bc = fb.centroid

            e1 = Edge(bc, ac)
            e2 = Edge(ac, bc)

            Edge.neighbours(e1, e2)

            self.tiles.setdefault(
                p1, Tile()
            ).add_edge(e1)
            self.tiles[p1].center = p1
            self.tiles.setdefault(
                p2, Tile()
            ).add_edge(e2)
            self.tiles[p2].center = p2

        for t in self.tiles.values():
            t.postprocess()

        self.tiles = sorted(self.tiles.values(), key=lambda t: len(t.edges))
        self.faces = []

    def _emit_vertices(self):
        vertices = []
        for vertex in _Point._container:
            vertices.extend((vertex.x, vertex.y, vertex.z))
        return vertices

    def _emit_faces(self):
        indicies = []
        for tile in self.tiles:
            indicies.extend(tile.emit_faces())
        return indicies

    def _emit_mesh(self):
        indicies = []
        for p1, p2 in Edge._container:
            indicies.extend((p1, p2))
        return indicies

    def emit(self):
        return {
            'position': self._emit_vertices(),
            'indicies': self._emit_faces(),
            'mesh': self._emit_mesh()
        }


if __name__ == '__main__':
    import sys
    subdiv = int(sys.argv[1])
    sphere = HexSphere(subdiv=subdiv)
    sphere.emit()
