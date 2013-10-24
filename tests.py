# encoding=utf-8

import unittest

from lightcycle.arena import LightCycleArena
from lightcycle.basebot import LightCycleBaseBot, LightCycleRandomBot
from lightcycle.player import Player
from lightcycle.security import blacklisted_modules

class TestArena(unittest.TestCase):

    def setUp(self):
        self.player1 = Player('Player 1', LightCycleRandomBot)
        self.player2 = Player('Player 2', LightCycleRandomBot)
        self.width = 10
        self.height = 10

    def test_regular_match(self):
        match = LightCycleArena((self.player1, self.player2), self.width, self.height).start()
        # Ojo que si los dos crashean, el test da un error que no deberia (EMPATE)
        print match
        self.assertIn('winner', match['result'], 'There should be a winner')
        self.assertEqual(match['result']['lost'].values(), ['Crashed'], 'The loser should have crashed')

    def test_string_bot_class(self):
        botsrc = ('''class LightCycleRandomBot(LightCycleBaseBot):\n'''
                  '''    def get_next_step(self, *args, **kwargs):\n'''
                  '''        return "N"''')
        player3 = Player('Player 3', botsrc)
        player4 = Player('Player 4', botsrc)
        match = LightCycleArena((player3, player4), self.width, self.height).start()
        self.assertEqual(match['result']['lost'].values(), ['Crashed'], 'The loser should have crashed')

    def test_invalid_bot_inheritance(self):
        class InvalidBot(object):
            pass
        player3 = Player('Player 3', InvalidBot)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.username)
        self.assertEqual(match['result']['lost'][player3.username].startswith('Exception'), True, 'Player 3 should raise an exception')

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
        self.assertNotIn('winner', match['result'])

    def test_invalid_move(self):
        class InvalidMoveBot(LightCycleBaseBot):
            def get_next_step(self, *args, **kwargs):
                return 'The 3rd dimension!'
        player3 = Player('Player 3', InvalidMoveBot)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.username)
        self.assertEqual(match['result']['lost'], {player3.username: 'Invalid output'}, 'Player 3 should return invalid output')

    def test_timeout_on_instantiation(self):
        import time
        class LightCycleDelay(LightCycleRandomBot):
            def __init__(self, *args, **kwargs):
                time.sleep(10)
                super(LightCycleDelay, self).__init__(*args, **kwargs)
        player3 = Player('Player 3', LightCycleDelay)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.username)
        self.assertEqual(match['result']['lost'], {player3.username: 'Timeout'}, 'Player 3 should timeout on instantiation')

    def test_timeout_on_move(self):
        import time
        class LightCycleDelay(LightCycleRandomBot):
            def get_next_step(self, *args, **kwargs):
                time.sleep(10)
                return super(LightCycleDelay, self).get_next_step(*args, **kwargs)
        player3 = Player('Player 3', LightCycleDelay)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.username)
        self.assertEqual(match['result']['lost'], {player3.username: 'Timeout'}, 'Player 3 should timeout on move')

    def test_bot_crash_on_init(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def __init__(self, *args, **kwargs):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.username)
        self.assertEqual(match['result']['lost'][player3.username], 'Exception (integer division or modulo by zero)', 'Player 3 should timeout due to a crash')

    def test_bot_crash_on_move(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def get_next_step(self, *args, **kwargs):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        match = LightCycleArena((self.player1, player3), self.width, self.height).start()
        self.assertEqual(match['result']['winner'], self.player1.username)
        self.assertEqual(match['result']['lost'][player3.username], 'Exception (integer division or modulo by zero)', 'Player 3 should timeout due to a crash')

    def test_tie(self):
        class BrokenLightCycle(LightCycleRandomBot):
            def get_next_step(self, *args, **kwargs):
                return 1/0
        player3 = Player('Player 3', BrokenLightCycle)
        player4 = Player('Player 4', BrokenLightCycle)
        match = LightCycleArena((player3, player4), self.width, self.height).start()
        self.assertNotIn('winner', match['result'])
        self.assertEqual(match['result']['lost'],
                         {player3.username: 'Exception (integer division or modulo by zero)',
                          player4.username: 'Exception (integer division or modulo by zero)'},
                         'Players 3 and 4 should both timeout simultaneously due to a crash (it was a tie)')

    def test_attacks(self):
        import random
        m = random.choice(blacklisted_modules)
        botsrc = ('''class LightCycleRandomBot(LightCycleBaseBot):\n'''
                  '''    def get_next_step(self, *args, **kwargs):\n'''
                  '''        import %s;return "N"''' % m)
        player3 = Player('Player 3', botsrc)
        player4 = Player('Player 4', botsrc)
        match = LightCycleArena((player3, player4), self.width, self.height).start()
        self.assertEqual(match['result']['lost'],
                         {player3.username: 'Exception (No module named %s)' % m,
                          player4.username: 'Exception (No module named %s)' % m},
                         'Players 3 and 4 should both timeout simultaneously due to an invalid import')
