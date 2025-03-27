from abc import ABC, abstractmethod
from ..utils import Card, GameState


class Player(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def make_move(
        self, player_id: int, candidate_moves: list[list[Card]], state: GameState
    ) -> int: ...
