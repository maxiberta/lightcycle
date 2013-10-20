# encoding=utf-8

import numpy

from .basebot import DIRECTIONS
from .worker import RemoteInstance


class LightCycleArena(object):

    def __init__(self, players, width=100, height=100):
        self.width = width
        self.height = height
        self.players = players
        self.setup()

    def setup(self):
        self.arena = numpy.zeros(shape=(self.width, self.height), dtype=numpy.int8)
        for i, player in enumerate(self.players, 1):
            player.color = i
            player._remote = RemoteInstance(player.bot)
            x = self.width * i / (len(self.players) + 1)
            y = self.height * i / (len(self.players) + 1)
            self.move(player, x, y)

    def move(self, player, x, y):
        #print player.name, '==>', x, y
        assert(player in self.players)
        assert(0 <= x < self.width)
        assert(0 <= y < self.height)
        assert(not self.arena[x, y])
        player.x = x
        player.y = y
        self.arena[player.x, player.y] = player.color
        print self.arena.T
        print

    def start(self):
        try:
            for step in xrange(self.width * self.height):
                for player in self.players:
                    arena_snapshot = self.arena.copy()
                    movement = player._remote.get_next_step(arena_snapshot, player.x, player.y)  # TODO add timeout!
                    #print player.name, '==>', movement
                    x = player.x + DIRECTIONS[movement].x
                    y = player.y + DIRECTIONS[movement].y
                    self.move(player, x, y)
        except RemoteInstance.Timeout:
            print 'TIME UP!',player.name
        except:
            print 'CRASHED!', player.name
        finally:
            for player in self.players:
                player._remote.terminate()
