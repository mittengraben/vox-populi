"""World object"""
from .hexsphere import HexSphere


class World(object):
    def __init__(self, config):
        self.geometry = HexSphere(subdiv=config.get('world_subdiv', 4)).emit()

    def get_geometry(self):
        return self.geometry
