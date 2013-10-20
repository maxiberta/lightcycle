# encoding=utf-8

from collections import namedtuple


Point = namedtuple('Point', 'x y')

DIRECTIONS = {
    'N': Point(0, -1),
    'E': Point(1, 0),
    'S': Point(0, 1),
    'W': Point(-1, 0),
}


class LightCycleBaseBot(object):

    def get_next_step(self, arena, x, y):
        raise NotImplementedError('Should return one Direction.')


class LightCycleRandomBot(LightCycleBaseBot):

    def get_next_step(self, arena, x, y):
        possible_directions = [key for key, direction in DIRECTIONS.items()
                               if 0 <= x + direction.x < arena.shape[0]
                               and 0 <= y + direction.y < arena.shape[1]
                               and not arena[x + direction.x, y + direction.y]]
        #print possible_directions
        import random
        return random.choice(possible_directions or DIRECTIONS.keys())
