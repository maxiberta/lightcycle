from lightcycle.arena import LightCycleArena
from lightcycle.basebot import LightCycleRandomBot, LightCycleRandomDelay
from lightcycle.player import Player


p1 = Player('Player 1', LightCycleRandomBot)
p2 = Player('Player 2', LightCycleRandomDelay)
p3 = Player('Player 3', LightCycleRandomBot)

arena = LightCycleArena((p1,p2), width=30, height=20)
arena.start()
