from copy import deepcopy
import math
import random

import torch
from torch import nn, tensor, Tensor

from ..abstract import Bot
from capsa.logging import cprint
from capsa.utils import (
    Card,
    GameState,
    copyGameState,
    createBotFeatures1,
    display_cards,
    generateCandidateMoves,
    simulateMove,
    valueOfPack,
)


def find_liabilities_and_stoppers(player_id: int, state: GameState, cutoff: float):
    """
    Liabilities are cards that are weaker that `cutoff` percent of the unplayed cards.
    Stoppers are cards that are stronger than `cutoff` percent of the unplayed cards.
    """

    unplayed_cards: list[Card] = []
    cards_in_hand: list[Card] = []

    for cvalue in range(2, 15):  # 3, 4 ... A, 2
        for csuit in range(4):  # ♦, ♣, ♥, ♠
            card_idx = (cvalue % 13) + (csuit * 13)

            if state.cards[card_idx] == 4:  # card is played
                continue

            if state.cards[card_idx] == player_id:  # card in player's hand
                cards_in_hand.append((cvalue, csuit))

            unplayed_cards.append((cvalue, csuit))

    cutoff_idx = math.ceil(len(unplayed_cards) * cutoff)
    liabilities = unplayed_cards[:cutoff_idx]
    stoppers = unplayed_cards[cutoff_idx:]

    liabilities_in_hand = set(liabilities) & set(cards_in_hand)
    stoppers_in_hand = set(stoppers) & set(cards_in_hand)

    return liabilities_in_hand, stoppers_in_hand


def compute_hand_relative_worth(
    player_id: int, state: GameState, good_packs: list[list[Card]]
):
    """
    Compute the average worth of a player's hand relative to the unplayed cards.
    Card worth = cvalue + 0.125 * csuit

    [Scenario 1]
    Card in Hand: 5♦ 5♣ 5♠ 7♣ 7♥
                  4♥ 6♦ 9♣ Q♥ K♠ 2♥

    Playing 4♥ still leaves the player with smaller average worth in hand, however
    5♦ 5♣ 5♠ 7♣ 7♥ is a good pack, it should not be considered as low worth.

    So instead of only computing the average worth of the whole hand, we need also
    to compute the average worth of the hand without each pack.

    [Scenario 2]
    Hand 1: 3♣ 5♣ 8♣ J♣ K♣
    Hand 2: 3♥ 5♣ 8♣ J♣ K♣

    Hand 1 should have higher average worth than Hand 2, because it can form a flush.
    """

    cards_in_hand = 0
    cards_in_hand_worth = 0.0

    cards_unplayed = 0
    cards_unplayed_worth = 0.0

    for cvalue in range(2, 15):  # 3, 4 ... A, 2
        for csuit in range(4):  # ♦, ♣, ♥, ♠
            card_idx = (cvalue % 13) + (csuit * 13)

            if state.cards[card_idx] == 4:  # card is played
                continue

            worth = cvalue + 0.125 * csuit
            cards_unplayed += 1
            cards_unplayed_worth += worth

            if state.cards[card_idx] == player_id:  # card in player's hand
                cards_in_hand += 1
                cards_in_hand_worth += worth

    # --- Might need to remove packs from the calculation --- #

    if cards_in_hand == 0 or cards_unplayed == 0:
        return 1.0

    average_hand_worth = cards_in_hand_worth / cards_in_hand
    average_unplayed_worth = cards_unplayed_worth / cards_unplayed

    # for pack in good_packs:
    #     if len(pack) == cards_in_hand:
    #         # todo: check how to handle this
    #         continue

    #     pack_worth = sum(cvalue + 0.125 * csuit for cvalue, csuit in pack)
    #     remaining_worth = cards_in_hand_worth - pack_worth
    #     remaining_cards = cards_in_hand - len(pack)

    #     average_hand_worth += remaining_worth

    return average_hand_worth - average_unplayed_worth


def find_good_packs(
    player_id: int, state: GameState, stoppers: set[Card], liabilities: set[Card]
):
    """
    Find good packs from the candidate moves.
    A good pack is a pack that uses more weaker cards than stronger ones.
    """

    state_ = copyGameState(state)
    state_.lastPlayedCards = []

    good_packs: list[list[Card]] = []
    candidate_moves = generateCandidateMoves(player_id, state_)

    for move in candidate_moves:
        if len(move) == 2:
            good_packs.append(move)

        elif len(move) == 5:
            stoppers_used = sum(1 for card in move if card in stoppers)
            liabilities_used = sum(1 for card in move if card in liabilities)

            if stoppers_used < liabilities_used:
                good_packs.append(move)

    return good_packs


def count_num_packs_broken(move: list[Card], good_packs: list[list[Card]]):
    """
    1. Scenario: 5♦ 5♣ 5♠ 7♣ 7♥
       It would be more acceptable to play 7♣ 7♥ than 7♣.
       It is debatable if playing 5♦ 5♣ is better than playing 5♦.
    2. Scenario: 5♦ 5♣ 6♠ 7♣ 8♥ 9♣
       Playing 5♦ 5♣ is a bad move, however playing 5♦ is good in most case.
    """

    num_broken = 0

    if len(move) == 0:
        return 0

    for good_pack in good_packs:
        if set(good_pack) & set(move):
            num_broken += 1

    return num_broken / len(move)


def move_reward(
    player_id: int,
    state: GameState,
    result_state: GameState,
    candidate_moves: list[list[Card]],
    move_idx: int,
):
    score: dict[str, float] = {}
    move = candidate_moves[move_idx]
    # move_type, move_value = valueOfPack(move)

    # # If the move is a pass, return 0.
    # # - If the card at hand is good, the model can exploit short-term rewards by not playing anything.
    # #   So we should not give any reward for passing.
    # # - In some cases, passing is a good move even when there is a playable card at hand.
    # #   So we should minimize penalize passing.
    # if len(move) == 0:
    #     return 0

    # Count the number of stopper and liable cards in the result state
    # - Stoppers are cards that are less likely to be contested by other players
    # - Liabilities are cards that has less chance of being played
    # pros: encourages the model to throw away liable cards.
    # cons: the model will more likely keep stopper cards in hand when there are a lot of liabilities,
    #       which can be either good or bad depending on the game state.
    liabilities, stoppers = find_liabilities_and_stoppers(player_id, result_state, 0.80)
    score_liabilities = len(liabilities) * 0.1
    score_stoppers = len(stoppers) * 0.35
    score["stopper_vs_liable"] = score_stoppers - score_liabilities

    # Punish the model for breaking stronger packs
    # pros: encourages the model to save cards that can form stronger packs
    # cons: the model would not break strong packs even when it is necessary to do so.
    good_packs = find_good_packs(player_id, state, stoppers, liabilities)
    num_packs_broken = count_num_packs_broken(move, good_packs)
    score["packs_broken"] = -num_packs_broken * 0.75

    # Reward the model if the average worth of the player's hand is higher than the average worth of the unplayed cards
    # pros: encourages the model to first throw away cards that are worth less.
    # cons: the model will less likely play cards that is worth higher than the average worth of the unplayed cards.
    #       because it will lower down the average worth of cards in hand more than it lowers down the average worth of
    #       unplayed cards.
    hand_relative_worth = compute_hand_relative_worth(
        player_id, result_state, good_packs
    )
    score["hand_relative_worth"] = hand_relative_worth * 5.0

    # Reward the model for having less cards in hand
    # pros: encourages the model to play cards when it can.
    # cons: the model can throw away strong cards just to reduce the number of cards in hand
    cards_in_hand = result_state.countPlayerCards(player_id)
    score["cards_in_hand"] = (1 - cards_in_hand / 13) * 1.25

    return sum(score.values()), score


def result_reward(rank: int):
    # todo: we can also compute the remaining cards in player hand to determine the final reward
    return (2, 0, 0, -2)[rank]


class StateEvalModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.fc1 = nn.Linear(110, 64)
        self.do1 = nn.Dropout(0.3)

        self.fc2 = nn.Linear(64, 16)
        self.do2 = nn.Dropout(0.2)

        self.fc3 = nn.Linear(16, 8)
        self.do3 = nn.Dropout(0.1)

        self.fc4 = nn.Linear(8, 1)
        self.relu = nn.LeakyReLU(0.02)

        self.loss = nn.MSELoss()

    def forward(self, X: Tensor) -> Tensor:
        o = self.relu(self.do1(self.fc1(X)))
        o = self.relu(self.do2(self.fc2(o)))
        o = self.relu(self.do3(self.fc3(o)))
        o = self.fc4(o)
        return o.flatten()


class StateEvalBot(Bot):
    def __init__(
        self,
        name: str,
        show_cards: bool = False,
        *,
        train: bool = False,
        memory_size: int = 100,
        exploration_rate: float = 1.0,
        exploration_decay: float = 0.995,
        exploration_k: int = 5,
        exploration_min: float = 0.05,
        discount_factor: float = 0.95,
    ):
        super().__init__(name, show_cards)
        self.model = StateEvalModel()
        self._loss = 0

        # Training parameters
        self.train = train
        self.exp_rate = exploration_rate  # exploration initial rate
        self.exp_decay = exploration_decay  # decay rate for exploration
        self.exp_k = exploration_k  # number of top moves to consider for exploration
        self.exp_min = exploration_min  # exploration rate lower bound
        self.discount_factor = discount_factor  # discount factor for future rewards

        # Training memory
        self.move_num: int = 0  # Number of moves made in the current game
        self.memory_idx: int = 0
        self.memory_size: int = memory_size
        self.memory_X: Tensor = torch.zeros((memory_size, 110), dtype=torch.float32)
        self.memory_y: Tensor = torch.zeros((memory_size,), dtype=torch.float32)

    def register_memory(self, x: list[float], y: float):
        self.memory_idx = self.memory_idx % self.memory_size
        self.memory_X[self.memory_idx] = tensor(x, dtype=torch.float32)
        self.memory_y[self.memory_idx] = y
        self.memory_idx += 1

    def select_move(self, candidate_moves: list[list[Card]], prediction: Tensor) -> int:
        # nb: if not in training mode, we choose the best move based on model prediction
        if not self.train:
            return prediction.argmax().item()

        # nb: in training mode, there is a self.exp_rate chance of exploring other moves
        if random.random() > self.exp_rate:
            return prediction.argmax().item()

        # # nb: in exploration, we sample `exp_k` moves based on their predicted probabilities.
        # #     higher probability means higher chance of being selected for exploration.
        # # nb: subtract prediction[i] by prediction.max() for numerical stability
        # proba = torch.softmax(prediction - prediction.max(), dim=0)
        # samples = min(len(candidate_moves), self.exp_k)
        # exploration_idx: list[int] = torch.multinomial(proba, samples, False).tolist()
        # return exploration_idx[0]

        # nb: use pure randomness for exploration
        return random.choice(range(len(candidate_moves)))

    def make_move(self, player_id, candidate_moves, state):
        super().make_move(player_id, candidate_moves, state)

        with torch.no_grad():
            result_states = [simulateMove(player_id, state, m) for m in candidate_moves]
            features = [createBotFeatures1(player_id, state) for state in result_states]
            prediction: Tensor = self.model(tensor(features, dtype=torch.float32))
            best_move = self.select_move(candidate_moves, prediction)

        # nb: register the move in the model memory
        if self.train:
            move_features = features[best_move]
            move_value, scores = move_reward(
                player_id, state, result_states[best_move], candidate_moves, best_move
            )
            self.register_memory(move_features, move_value)

        elif self.show_cards:
            # temporary for debugging
            for i, (candidate_move, model_prediction) in enumerate(
                zip(candidate_moves, prediction)
            ):
                cprint(f"{i}.", end=" ")
                display_cards(candidate_move, end=" | ")
                cprint(f"Prediction: {model_prediction.item():.3f}", end=" | ")

                move_value, scores = move_reward(
                    player_id, state, result_states[i], candidate_moves, i
                )
                cprint(f"Move Reward: {move_value:.3f}", end=" | ")
                cprint(f"Rewards Breakdown: {scores}")

        self.move_num += 1
        return best_move

    def on_game_start(self):
        self.move_num = 0

    def on_game_end(self, rank: int):
        if self.train:
            reward = result_reward(rank)

            # nb: incorporate the result reward into the moves played in current game
            #     - older moves has less influence on the result, so it gets less reward
            for i in range(self.move_num):
                idx = (self.memory_idx - 1 - i) % self.memory_size
                self.memory_y[idx] += reward
                reward *= self.discount_factor

            self._loss = self.fit(self.memory_X, self.memory_y)
            self.exp_rate = max(self.exp_min, self.exp_rate * self.exp_decay)

    def fit(self, X: Tensor, y: Tensor, epochs: int = 3, lr: float = 0.05):
        loss: Tensor | None = None
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.model.train()

        for _ in range(epochs):
            optimizer.zero_grad()
            output = self.model(X)
            loss: Tensor = self.model.loss(output, y)
            loss.backward()
            optimizer.step()

        return loss.item()

    def save_model(self, path: str):
        torch.save(self.model.state_dict(), path)

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path, weights_only=True))
