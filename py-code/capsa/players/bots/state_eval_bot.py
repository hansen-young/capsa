from collections import deque

import torch
from torch import nn, tensor, Tensor

from ..abstract import Bot
from ...utils import (
    Card,
    GameState,
    createBotFeatures1,
    simulateMove,
    valueOfPack,
    generateCandidateMoves,
)


def move_reward(
    player_id: int,
    state: GameState,
    result_state: GameState,
    candidate_moves: list[list[Card]],
    move_idx: int,
):
    score = 0
    move = candidate_moves[move_idx]
    move_type, move_value = None, None

    # Reward based on length of played cards
    score += 0.5 * len(move)

    # Reward for playing smaller cards first
    score_per_smaller_card = -0.75
    score_per_larger_card = 0.75

    if len(move) > 0:
        for cmove in candidate_moves:
            if len(cmove) != len(move) or len(cmove) == 0:
                continue

            if len(cmove) == 5:
                if not move_type or not move_value:
                    move_type, move_value = valueOfPack(move)

                if valueOfPack(cmove) >= (move_type, move_value):
                    score += score_per_larger_card
                else:
                    score += score_per_smaller_card

            elif max(move) < max(cmove):
                score += score_per_smaller_card
            elif max(move) > max(cmove):
                score += score_per_larger_card

    # Reward for the number of strong cards in hand
    strong_threshold = 9  # 10 and above is considered strong
    score_diff_multiplier = 0.1

    for card, owner in enumerate(result_state.cards):
        if owner != player_id:
            continue

        cvalue = card % 13
        cvalue = cvalue + 13 * (cvalue < 2)  # Convert A, 2 to 13, 14
        score += (cvalue - strong_threshold) * score_diff_multiplier

    # Punish playing small single cards that can be played as a pack
    score_per_packable_card = -0.5

    if len(move) == 1 and move[0][0] < strong_threshold:
        h_state = GameState()
        h_state.cards = state.cards
        h_state.lastPlayedCards = []
        h_candidate_moves = generateCandidateMoves(player_id, h_state)

        for cmove in h_candidate_moves:
            if len(cmove) != 5:
                continue

            if move[0] in cmove:
                score += score_per_packable_card

    return score


def result_reward(rank: int):
    return (15, 5, 5, -10)[rank]


class StateEvalModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.fc1 = nn.Linear(110, 64)
        self.fc2 = nn.Linear(64, 16)
        self.fc3 = nn.Linear(16, 1)
        self.relu = nn.ReLU()
        self.do = nn.Dropout(0.2)

        self.loss = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.parameters(), lr=0.01)

    def forward(self, X: Tensor) -> Tensor:
        o = self.fc1(X)
        o = self.relu(o)
        o = self.do(o)

        o = self.fc2(o)
        o = self.relu(o)
        o = self.do(o)

        o = self.fc3(o)
        return o

    def train(self, X: Tensor, y: Tensor, epochs: int = 10):
        loss: Tensor | None = None

        for _ in range(epochs):
            self.optimizer.zero_grad()
            output = self.forward(X).squeeze(-1)
            loss: Tensor = self.loss(output, y)
            loss.backward()
            self.optimizer.step()

        return loss.item()


class StateEvalBot(Bot):
    def __init__(self, name: str, show_cards: bool = False, train: bool = False):
        super().__init__(name, show_cards)
        self.model = StateEvalModel()
        self.memory_X: deque[list[float]] = deque(maxlen=1000)
        self.memory_y: deque[float] = deque(maxlen=1000)
        self.current_memory: list[tuple[list[float], float]] = []
        self.train = train
        self._loss = 0

    def make_move(self, player_id, candidate_moves, state):
        super().make_move(player_id, candidate_moves, state)

        with torch.no_grad():
            result_states = [simulateMove(player_id, state, m) for m in candidate_moves]
            features = [createBotFeatures1(player_id, state) for state in result_states]
            prediction: Tensor = self.model(tensor(features, dtype=torch.float32))
            best_move = prediction.argmax().item()

        if self.train:
            self.current_memory.append(
                (
                    features[best_move],
                    move_reward(
                        player_id,
                        state,
                        result_states[best_move],
                        candidate_moves,
                        best_move,
                    ),
                )
            )

        return best_move

    def on_game_start(self):
        if not self.train:
            return

        self.current_memory.clear()

    def on_game_end(self, rank: int):
        if not self.train:
            return

        reward = result_reward(rank)

        # Add moves from current game to memory
        for c in self.current_memory:
            self.memory_X.append(c[0])
            self.memory_y.append(c[1] + reward)

        # Train the model
        X = tensor(self.memory_X, dtype=torch.float32)
        y = tensor(self.memory_y, dtype=torch.float32)
        self._loss = self.model.train(X, y)

    def save_model(self, path: str):
        torch.save(self.model.state_dict(), path)

    def load_model(self, path: str):
        self.model.load_state_dict(torch.load(path, weights_only=True))
