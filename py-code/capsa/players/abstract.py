from abc import ABC, abstractmethod

from capsa.logging import cprint
from ..utils import Card, GameState, display_player_cards


class Player(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def make_move(
        self, player_id: int, candidate_moves: list[list[Card]], state: GameState
    ) -> int: ...

    def on_game_start(self):
        pass

    def on_game_end(self, rank: int):
        pass


class Bot(Player):
    def __init__(self, name: str, show_cards: bool = False):
        super().__init__(name)
        self.show_cards = show_cards

    def make_move(self, player_id, candidate_moves, state) -> int:
        if self.show_cards:
            cprint("\nCards in Hand:")
            display_player_cards(player_id, state)
            cprint()

        return 0
