from .abstract import Player
from ..utils import display_cards, display_player_cards


class HumanPlayer(Player):
    def make_move(self, player_id, candidate_moves, state):
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

        return move
