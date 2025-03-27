import random
from ..abstract import Player


class RandomBot(Player):
    def make_move(self, player_id, candidate_moves, state):
        return random.randint(0, len(candidate_moves) - 1)
