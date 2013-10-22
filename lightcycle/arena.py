# encoding=utf-8

import numpy

from .basebot import DIRECTIONS, LightCycleBaseBot
from .worker import RemoteInstance


class LightCycleArena(object):

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=100, height=100):
        self.width = width
        self.height = height
        self.players = players
        self.match = LightCycleMatch(width, height, players)
        self.setup()

    def setup(self):
        self.arena = numpy.zeros(shape=(self.width, self.height), dtype=numpy.int8)
        for i, player in enumerate(self.players, 1):
            player.color = i
            player.status = self.PLAYING
            player._botproxy = RemoteInstance(player.bot, timeout=.02, namespace={'LightCycleBaseBot':LightCycleBaseBot})
            x = self.width * i / (len(self.players) + 1)
            y = self.height * i / (len(self.players) + 1)
            self.move(player, x, y)

    def move(self, player, x, y, direction=None):
        #print player.name, '==>', x, y
        assert(player in self.players)
        assert(0 <= x < self.width)
        assert(0 <= y < self.height)
        player.x, player.y, player.direction = x, y, direction
        occupied = not self.arena[x, y]
        self.arena[player.x, player.y] = player.color
        self.match.log(player, player.x, player.y, direction)
        print self.arena.T
        print
        assert(occupied)

    def start(self):
        try:
            for step in xrange(self.width * self.height):
                playing = [player for player in self.players
                                    if player.status == self.PLAYING]
                # Check if there's just one player playing. That's the winner!
                if len(playing) == 0:
                    break  # A tie... Everybody loses :-(
                if len(playing) == 1:
                    self.match.winner(playing[0])
                    break  # There's one winner!! :-D
                for player in self.players:
                    arena_snapshot = self.arena.copy()
                    try:
                        movement = player._botproxy.get_next_step(arena_snapshot, player.x, player.y, player.direction)
                        if movement not in DIRECTIONS:
                            raise RemoteInstance.InvalidOutput()
                        #print player.name, '==>', movement
                        x = player.x + DIRECTIONS[movement].x
                        y = player.y + DIRECTIONS[movement].y
                        self.move(player, x, y, movement)
                    except RemoteInstance.InvalidOutput:
                        print 'Invalid output!', player.name, movement
                        self.match.lost(player, u'Invalid output')
                    except RemoteInstance.Timeout:
                        print 'TIME UP!', player.name
                        self.match.lost(player, u'Timeout')
                    except:
                        print 'CRASHED!', player.name, player.x, player.y
                        self.match.lost(player, u'Crashed')
        finally:
            import json
            print json.dumps(self.match.__json__())
            for player in self.players:
                player._botproxy.terminate()
            return self.match.__json__()


class LightCycleMatch(object):

    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.moves = []
        self.result = {}

    def log(self, player, x, y, direction=None):
        self.moves.append(dict(
            player=player.name,
            x=x,
            y=y,
            direction=direction,
        ))

    def winner(self, player):
        player.status = LightCycleArena.WINNER
        self.result['winner'] = player.name

    def lost(self, player, cause):
        player.status = LightCycleArena.LOST
        if 'lost' not in self.result:
            self.result['lost'] = {}
        self.result['lost'][player.name] = cause

    def __json__(self):
        data = dict(
                width=self.width,
                height=self.height,
                players=[player.name for player in self.players],
                moves=self.moves,
                result=self.result,
                )
        return data
