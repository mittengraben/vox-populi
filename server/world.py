"""World object"""
from .hexsphere import HexSphere


class World(object):
    def __init__(self):
        self.geometry = HexSphere(subdiv=4).emit()

    def get_geometry(self):
        return self.geometry
