# encoding=utf-8

import unittest

from lightcycle.arena import LightCycleArena
from lightcycle.basebot import LightCycleBaseBot, LightCycleRandomBot
from lightcycle.player import Player


class TestArena(unittest.TestCase):

    def setUp(self):
        self.player1 = Player('Player 1', LightCycleRandomBot)
        self.player2 = Player('Player 2', LightCycleRandomBot)
        self.width = 20
        self.height = 20

    def test_regular_match(self):
        match = LightCycleArena((self.player1, self.player2), self.width, self.height).start()
        self.assertEqual(match['result']['lost'].values(), ['Crashed'], 'The loser should have crashed')

    def test_string_bot_class(self):
        botsrc = ('''class LightCycleRandomBot(LightCycleBaseBot):\n'''
                  '''    def get_next_step(self, *args, **kwargs):\n'''
                  '''        return "N"''')
        player3 = Player('Player 3', botsrc)
        player4 = Player('Player 4', botsrc)
        match = LightCycleArena((player3, player4), self.width, self.height).start()
        self.assertEqual(match['result']['lost'].values(), ['Crashed'], 'The loser should have crashed')

    def test_bots_crashing_on_each_other(self):
        class EastBot(LightCycleBaseBot):
            def get_next_step(self, *args, **kwargs):
                return 'E'
        class WestBot(LightCycleBaseBot):
            def get_next_step(self, *args, **kwargs):
                return 'W'
        player3 = Player('Player 3', EastBot)
        player4 = Player('Player 4', WestBot)
        match = LightCycleArena((player3, player4), self.width, 1).start()
        self.assertEqual(len(match['result']['lost']), 2)

    def test_invalid_move(self):
        class InvalidMoveBot(LightCycleBaseBot):
            def get_next_step(self, *args, **kwargs):
                return 'The 3rd dimension!'
        player3 = Player('Player 3', InvalidMoveBot)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], {player3.name: 'Invalid output'}, 'Player 3 should return invalid output')

    def test_timeout_on_instantiation(self):
        import time
        class LightCycleDelay(LightCycleRandomBot):
            def __init__(self, *args, **kwargs):
                time.sleep(10)
                super(LightCycleDelay, self).__init__(*args, **kwargs)
        player3 = Player('Player 3', LightCycleDelay)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], {player3.name: 'Timeout'}, 'Player 3 should timeout on instantiation')

    def test_timeout_on_move(self):
        import time
        class LightCycleDelay(LightCycleRandomBot):
            def get_next_step(self, *args, **kwargs):
                time.sleep(10)
                return super(LightCycleDelay, self).get_next_step(*args, **kwargs)
        player3 = Player('Player 3', LightCycleDelay)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], {player3.name: 'Timeout'}, 'Player 3 should timeout on move')

    def test_bot_crash_on_init(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def __init__(self, *args, **kwargs):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], {player3.name: 'Timeout'}, 'Player 3 should timeout due to a crash')

    def test_bot_crash_on_move(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def get_next_step(self, *args, **kwargs):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.name)
        self.assertEqual(match['result']['lost'], {player3.name: 'Timeout'}, 'Player 3 should timeout due to a crash')

    def test_multiple_crashes(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def get_next_step(self, *args, **kwargs):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        player4 = Player('Player 4', BrokenLightCycle)
        match = LightCycleArena((player3, player4), self.width, self.height).start()
        self.assertNotIn('winner', match['result'])
        self.assertEqual(match['result']['lost'],
                         {player3.name: 'Timeout', player4.name: 'Timeout'},
                         'Players 3 and 4 should both timeout simultaneously due to a crash')
