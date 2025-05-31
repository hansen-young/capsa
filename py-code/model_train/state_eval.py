from uuid import uuid4
from tempfile import TemporaryDirectory

import mlflow
from tqdm import tqdm

from capsa import CapsaGame
from capsa import logging
from capsa.players.bots.state_eval_bot import StateEvalBot, StateEvalModel


def argsort(seq: list[float]):
    return sorted(range(len(seq)), key=seq.__getitem__)


class ModelTrainer:
    def evaluate(self, players: list[StateEvalBot], num_simulations: int = 100):
        """
        Evaluate the performance of the given players and return their models.
        """
        ranks = [0, 0, 0, 0]

        for player in players:
            player.train = False
            player.model.eval()

        game = CapsaGame(players)

        for _ in tqdm(range(num_simulations), desc="Evaluating Models"):
            game.start()

            for i, r in enumerate(game.ranks):
                ranks[i] += r

        return [r / num_simulations for r in ranks]

    def train(self):
        logging.disable_log()
        mlflow.set_tracking_uri("http://localhost:3000")
        mlflow.set_experiment("Model Training")

        with mlflow.start_run() as run:
            top3_models = [None, None, None]

            for generation in range(100):
                # Prepare players
                players = [StateEvalBot(f"g{generation}", train=True)]

                for model_name in top3_models:
                    if model_name is None:
                        model = StateEvalBot(f"dummy-{str(uuid4())[:8]}", train=False)
                    else:
                        model = StateEvalBot(model_name, train=False)

                        with TemporaryDirectory() as tmpdir:
                            path = mlflow.artifacts.download_artifacts(
                                artifact_uri=f"runs:/{run.info.run_id}/{model_name}.pt",
                                dst_path=tmpdir,
                            )
                            model.load_model(path)

                    players.append(model)

                game = CapsaGame(players)

                # Train model
                for step in tqdm(range(5000), desc=f"Training Gen {generation}"):
                    game.start()
                    mlflow.log_metric(
                        f"Generation-{generation}", players[0]._loss, step=step
                    )

                # Evaluate models
                model_performance = self.evaluate(players)
                sorted_indices = argsort(model_performance)
                top3_models = [
                    players[i].name if players[i].name.startswith("g") else None
                    for i in sorted_indices[:3]
                ]
                print(f"{sorted_indices=}, {top3_models=}")

                # Save model
                with TemporaryDirectory() as tmpdir:
                    players[0].save_model(f"{tmpdir}/{players[0].name}.pt")
                    mlflow.log_artifact(f"{tmpdir}/{players[0].name}.pt")
