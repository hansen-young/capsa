from capsa import CapsaGame
from capsa.players.bots.state_eval_bot import StateEvalBot, StateEvalModel


class StateEvalGroupTrainer:
    def __init__(self, model: StateEvalModel | None = None):
        self.model = model or StateEvalModel()
        self.players = [
            StateEvalBot("Bot1", train=True),
            StateEvalBot("Bot2", train=True),
            StateEvalBot("Bot3", train=True),
            StateEvalBot("Bot4", train=True),
        ]
        self.game = CapsaGame(self.players)
        self._init()

    def _init(self):
        for player in self.players:
            player.model = self.model

    def train(self, num_rounds: int = 10):
        for _ in range(num_rounds):
            self.game.start()

            losses = [p._loss for p in self.players]
            avg_loss = sum(losses) / len(losses)
            print(f"Loss: {avg_loss:.4f}")

    def save_model(self, path: str):
        bot = StateEvalBot(name="Bot")
        bot.model = self.model
        bot.save_model(path)

    def load_model(self, path: str):
        self.players[0].load_model(path)
        self.model = self.players[0].model
        self._init()
