from __future__ import annotations
import random

from .players import Player
from .utils import Card, GameState, display_cards, generateCandidateMoves
from .logging import cprint


NUM_PLAYERS = 4


class CapsaGame:

    def __init__(self, players: list[Player], keep_history: bool = False):
        self.players: list[Player] = players
        self.player_turn: int = 0
        self.state: GameState

        # History of game containing tuples of (player_id, GameState, played_cards)
        self.history: list[tuple[int, GameState, list[Card]]]
        self.ranks: list[int]

        self.reset()

    def reset(self):
        if len(self.players) != NUM_PLAYERS:
            raise ValueError(f"Number of players must be {NUM_PLAYERS}")

        self.state = GameState.createNewState()
        self.player_turn = self.state.lastMovePlayerId
        self.ranks = [-1] * NUM_PLAYERS

    def start_turn(self):
        self.state.clearLastPlayedCards()
        self.state.clearPlayerPassFlags()
        self.player_turn = self.state.lastMovePlayerId

        while True:
            if self.state.numPlayersPassed() >= NUM_PLAYERS - 1:
                break

            if not self.state.playerPassFlag[self.player_turn]:
                player = self.players[self.player_turn]
                cprint(f"[{player.name} Turn]")

                candidate_moves = generateCandidateMoves(self.player_turn, self.state)
                move = player.make_move(self.player_turn, candidate_moves, self.state)
                cprint(f"{player.name} played: ", end="")
                display_cards(candidate_moves[move])
                cprint("\n" + "=" * 20)

                self.state.update(self.player_turn, candidate_moves[move])

                if not self.state.activePlayerFlag[self.player_turn]:
                    rank = 3 - self.state.numActivePlayers()
                    self.ranks[self.player_turn] = rank
                    cprint(f"{player.name} finished rank {rank + 1}!")

            self.player_turn = (self.player_turn + 1) % NUM_PLAYERS

    def start(self):
        self.reset()

        for i, player in enumerate(self.players):
            player.on_game_start()

        while self.state.numActivePlayers() > 1:
            self.start_turn()

        for i, player in enumerate(self.players):
            if self.state.activePlayerFlag[i]:
                self.ranks[i] = 3
                cprint(f"{player.name} losts!")

            player.on_game_end(self.ranks[i])

        cprint("Game Over!")
