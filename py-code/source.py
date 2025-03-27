from capsa import CapsaGame, HumanPlayer, RandomBot

players = [
    HumanPlayer("Player 1"),
    RandomBot("Player 2"),
    RandomBot("Player 3"),
    RandomBot("Player 4"),
]
game = CapsaGame(players)
game.start()
