# encoding=utf-8

import unittest

from lightcycle.arena import LightCycleArena
from lightcycle.basebot import LightCycleBaseBot, LightCycleRandomBot
from lightcycle.player import Player


class TestArena(unittest.TestCase):

    def setUp(self):
        self.player1 = Player('Player 1', LightCycleRandomBot)
        self.player2 = Player('Player 2', LightCycleRandomBot)
        self.width = 30
        self.height = 20

    def test_regular_match(self):
        match = LightCycleArena((self.player1, self.player2), self.width, self.height).start()
        self.assertEqual(match['result']['lost'][0].values(), ['Crashed'], 'The loser should have crashed')

    def test_invalid_move(self):
        class InvalidMoveBot(LightCycleBaseBot):
            def get_next_step(self, *args, **kwargs):
                return 'The 3rd dimension!'
        player3 = Player('Player 3', InvalidMoveBot)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], [{player3.name: 'Invalid output'}], 'Player 3 should return invalid output')

    def test_timeout_on_instantiation(self):
        import time
        class LightCycleDelay(LightCycleRandomBot):
            def __init__(self, *args, **kwargs):
                time.sleep(10)
                super(LightCycleDelay, self).__init__(*args, **kwargs)
        player3 = Player('Player 3', LightCycleDelay)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], [{player3.name: 'Timeout'}], 'Player 3 should timeout on instantiation')

    def test_timeout_on_move(self):
        import time
        class LightCycleDelay(LightCycleRandomBot):
            def get_next_step(self, arena, x, y):
                time.sleep(10)
                return super(LightCycleDelay, self).get_next_step(arena, x, y)
        player3 = Player('Player 3', LightCycleDelay)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], [{player3.name: 'Timeout'}], 'Player 3 should timeout on move')

    def test_bot_crash(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def get_next_step(self, arena, x, y):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], [{player3.name: 'Timeout'}], 'Player 3 should timeout due to a crash')
