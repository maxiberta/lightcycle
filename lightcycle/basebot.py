# encoding=utf-8

from collections import namedtuple


Point = namedtuple('Point', 'id x y')

DIRECTIONS = {
    'N': Point('N', 0, -1),
    'E': Point('E', 1, 0),
    'S': Point('S', 0, 1),
    'W': Point('W', -1, 0),
}


class LightCycleBaseBot(object):

    def get_next_step(self, arena, x, y):
        raise NotImplementedError('Should return one Direction.')


class LightCycleRandomBot(LightCycleBaseBot):

    def get_next_step(self, arena, x, y):
        possible_directions = [direction.id for direction in DIRECTIONS.values()
                               if 0 <= x + direction.x < arena.shape[0]
                               and 0 <= y + direction.y < arena.shape[1]
                               and not arena[x + direction.x, y + direction.y]]
        #print possible_directions
        import random
        return random.choice(possible_directions or DIRECTIONS.keys())
