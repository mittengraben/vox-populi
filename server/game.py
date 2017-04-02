import collections

from .player import Player
from .timers import Timers
from .world import World

instance = None


_Task = collections.namedtuple('_Task', ['target', 'action', 'args', 'after'])


class Game(object):
    def __init__(self, conf):
        self.timers = Timers()
        self.world = World(conf)
        self.players = []

    def add_players(self):
        self.players = [Player(0)]

    def schedule(self, **kwargs):
        self.timers.schedule(_Task(**kwargs))

    def dispose(self):
        self.timers.stop()
