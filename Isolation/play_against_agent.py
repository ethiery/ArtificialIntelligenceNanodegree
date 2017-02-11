from isolation import Board
from sample_players import HumanPlayer
from game_agent import CustomPlayer

TIME_LIMIT = 150  # number of milliseconds before timeout


def main():
    player_1 = HumanPlayer()
    player_2 = CustomPlayer(method='alphabeta', iterative=True)
    game = Board(player_1, player_2)

    winner, _, termination = game.play(time_limit=TIME_LIMIT)
    if player_1 == winner:
        print("You win")
        if termination == "timeout":
            print("because the AI timed out")

    elif player_2 == winner:
        print("You loose")

if __name__ == "__main__":
    main()
