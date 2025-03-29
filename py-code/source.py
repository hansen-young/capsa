from capsa import CapsaGame
from capsa.players.bots import RandomBot

players = [
    RandomBot("Player 1"),
    RandomBot("Player 2"),
    RandomBot("Player 3"),
    RandomBot("Player 4"),
]
game = CapsaGame(players)
game.start()
