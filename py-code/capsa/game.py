from __future__ import annotations
import random
from abc import ABC, abstractmethod
from typing import TypeAlias

from .c_utils import GameState, generateCandidateMoves


Card: TypeAlias = tuple[int, int]  # (value, suit)
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["♦", "♣", "♥", "♠"]


def cardToString(card: Card):
    value = CARD_VALUES[card[0] % 13]
    suit = CARD_SUITS[card[1]]
    return f"{value}{suit}"


def display_cards(cards: list[Card]):
    for card in cards:
        print(cardToString(card), end=" ")
    print()


def display_player_cards(player_id: int, state: GameState):
    cards = []

    for i, owner in enumerate(state.cards):
        if owner == player_id:
            cards.append((i, i // 13))

    display_cards(cards)


class Player(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def make_move(
        self, player_id: int, candidate_moves: list[list[Card]], state: GameState
    ) -> int: ...


class HumanPlayer(Player):
    def make_move(self, player_id, candidate_moves, state):
        print(f"[{self.name} Turn]")

        print("Last Played Cards: ", end="")
        display_cards(state.lastPlayedCards)

        print("\nCards in Hand:")
        display_player_cards(player_id, state)

        print("\nCandidate Moves:")
        for i, move in enumerate(candidate_moves):
            print(f"{i}. ", end="")
            display_cards(move)

        move = -1
        while move < 0 or move >= len(candidate_moves):
            try:
                move = int(input("Enter move: "))
            except Exception:
                pass

        print(f"\n{self.name} played: ", end="")
        display_cards(candidate_moves[move])
        print("\n" + "=" * 20)

        return move


class BotPlayer(Player):
    def make_move(self, player_id, candidate_moves, state):
        print(f"[{self.name} Turn]")
        move = random.randint(0, len(candidate_moves) - 1)
        print(f"{self.name} played: ", end="")
        display_cards(candidate_moves[move])
        print("\n" + "=" * 20)
        return move


class CapsaGame:
    NUM_PLAYERS = 4

    def __init__(self, players: list[Player]):
        self.players: list[Player] = players
        self.player_turn: int = 0
        self.state: GameState
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

    def start_turn(self):
        self.state.clearLastPlayedCards()
        self.state.clearPlayerPassFlags()
        self.player_turn = self.state.lastMovePlayerId

        while True:
            if self.state.numPlayersPassed() >= self.NUM_PLAYERS - 1:
                break

            if not self.state.playerPassFlag[self.player_turn]:
                player = self.players[self.player_turn]
                candidate_moves = generateCandidateMoves(self.player_turn, self.state)
                move = player.make_move(self.player_turn, candidate_moves, self.state)
                self.state.update(self.player_turn, candidate_moves[move])

            self.player_turn = (self.player_turn + 1) % self.NUM_PLAYERS

    def start(self):
        while self.state.numActivePlayers() > 1:
            self.start_turn()

        for i, is_active in enumerate(self.state.activePlayerFlag):
            if is_active:
                print(f"{self.players[i].name} losts!")

        print("Game Over!")

    def _validate_attrs(self):
        if len(self.players) != self.NUM_PLAYERS:
            raise ValueError(f"Number of players must be {self.NUM_PLAYERS}")
