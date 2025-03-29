from typing import TypeAlias
from .c_utils import (
    GameState,
    createBotFeatures1,
    generateCandidateMoves,
    simulateMove,
    valueOfPack,
)
from .logging import cprint

Card: TypeAlias = tuple[int, int]  # (value, suit)
CARD_VALUES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
CARD_SUITS = ["♦", "♣", "♥", "♠"]


def cardToString(card: Card):
    value = CARD_VALUES[card[0] % 13]
    suit = CARD_SUITS[card[1]]
    return f"{value}{suit}"


def display_cards(cards: list[Card]):
    for card in cards:
        cprint(cardToString(card), end=" ")
    cprint()


def display_player_cards(player_id: int, state: GameState):
    cards = []

    for i, owner in enumerate(state.cards):
        if owner == player_id:
            cards.append((i, i // 13))

    display_cards(cards)
