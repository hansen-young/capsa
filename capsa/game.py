from __future__ import annotations
import random

from .players import Player
from .utils import GameState, display_cards, generateCandidateMoves
from .logging import cprint


class CapsaGame:
    NUM_PLAYERS = 4

    def __init__(self, players: list[Player]):
        self.players: list[Player] = players
        self.player_turn: int = 0
        self.state: GameState
        self.ranks: list[int]
        self.reset()

    def generate_new_gamestate(self):
        state = GameState()

        # nb: don't do random.shuffle(state.cards) because state is a
        #     c++ object and for some reason it doesn't work
        cards = [i for i in range(self.NUM_PLAYERS)] * 13
        random.shuffle(cards)

        state.cards = cards
        state.lastMovePlayerId = cards[2]  # 3♦ owner

        return state

    def reset(self):
        self._validate_attrs()
        self.state = self.generate_new_gamestate()
        self.player_turn = self.state.lastMovePlayerId
        self.ranks = [-1] * self.NUM_PLAYERS

    def start_turn(self):
        self.state.clearLastPlayedCards()
        self.state.clearPlayerPassFlags()
        self.player_turn = self.state.lastMovePlayerId

        while True:
            if self.state.numPlayersPassed() >= self.NUM_PLAYERS - 1:
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

            self.player_turn = (self.player_turn + 1) % self.NUM_PLAYERS

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

    def _validate_attrs(self):
        if len(self.players) != self.NUM_PLAYERS:
            raise ValueError(f"Number of players must be {self.NUM_PLAYERS}")
