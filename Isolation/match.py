from isolation import Board
from sample_players import HumanPlayer
from game_agent import CustomPlayer
from game_agent import custom_score

TIME_LIMIT = 150  # number of milliseconds before timeout



def main():
    player1 = HumanPlayer()
    player2 = CustomPlayer(score_fn=custom_score, method='alphabeta', iterative=True)
    game = Board(player1, player2)

    winner, move_history, termination = game.play(time_limit=TIME_LIMIT)
    if player1 == winner:
        print("You win")
        if termination == "timeout":
            print("because the AI timed out")

    elif player2 == winner:
        print("You loose")

if __name__ == "__main__":
    main()
