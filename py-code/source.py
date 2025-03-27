from capsa import CapsaGame, HumanPlayer, BotPlayer

players = [
    HumanPlayer("Player 1"),
    BotPlayer("Player 2"),
    BotPlayer("Player 3"),
    BotPlayer("Player 4"),
]
game = CapsaGame(players)
game.start()
