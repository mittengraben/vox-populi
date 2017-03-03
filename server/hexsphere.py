"""Hexsphere generator"""
import math


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

    def __repr__(self):
        return '<Point {}>'.format(
            self.index, self.x, self.y, self.z
        )

    def reproject(self):  # i.e. normalize
        magnitude = math.sqrt(
            self.x * self.x +
            self.y * self.y +
            self.z * self.z
        )
        self.x = self.x / magnitude
        self.y = self.y / magnitude
        self.z = self.z / magnitude

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


class _Tile(object):
    __slots__ = ['triangles', 'id']

    def __init__(self, identifier):
        super(_Tile, self).__init__()
        self.triangles = []
        self.id = identifier


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
        new_faces = []

        for p1, p2, fa, fb in self._make_face_pairs():
            ac = fa.centroid
            bc = fb.centroid

            f1 = _Face(p1, bc, ac)
            f2 = _Face(p2, ac, bc)

            new_faces.append(f1)
            new_faces.append(f2)

            self.tiles.setdefault(
                p1, _Tile(p1)
            ).triangles.append(f1)
            self.tiles.setdefault(
                p2, _Tile(p2)
            ).triangles.append(f2)

        self.faces = new_faces

    def _emit_vertices(self, name='hexsphere_position'):
        print('var {} = new Float32Array(['.format(name))
        for vertex in _Point._container:
            print(
                '\t{:.6g}, {:.6g}, {:.6g},'
                .format(vertex.x, vertex.y, vertex.z)
            )
        print(']);')

    def _emit_faces(self, name='hexsphere_indicies'):
        print('var {} = new Uint32Array(['.format(name))
        for face in self.faces:
            print(
                '\t{}, {}, {},'
                .format(face.v1, face.v2, face.v3)
            )
        print(']);')

    def emit(self):
        self._emit_vertices()
        self._emit_faces()


if __name__ == '__main__':
    import sys
    subdiv = int(sys.argv[1])
    sphere = HexSphere(subdiv=subdiv)
    sphere.emit()
