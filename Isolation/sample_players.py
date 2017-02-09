from isolation import Player, Board, Move, Timer
from typing import List, Callable
from random import choice

Score_Function = Callable[[Board, Player], float]


def null_score(game: Board, player: Player) -> float:
    """
    This heuristic presumes no knowledge for non-terminal states, and
    returns the same uninformative value for all other states.

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game.

    player : One of the registered player of the current game

    Returns
    ----------
    float
        The heuristic value of the current game state.
    """
    return game.utility(player)


def open_move_score(game: Board, player: Player) -> float:
    """
    This heuristic returns a score equal to the number of moves open for a given player on the board.

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game.

    player : One of the registered player of the current game

    Returns
    ----------
    The heuristic value of the current game state
    """
    utility = game.utility(player)
    if utility != 0:
        return utility

    return float(len(game.get_legal_moves(player)))


def improved_score(game: Board, player: Player):
    """
    This heuristic outputs a score equal to the difference in the number of moves available to the two players.

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game.

    player : One of the registered player of the current game

    Returns
    ----------
    The heuristic value of the current game state
    """
    utility = game.utility(player)
    if utility != 0:
        return utility

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - opp_moves)


class RandomPlayer(Player):
    """Player that chooses a move randomly."""

    def get_move(self, game: Board, legal_moves: List[Move], time_left: Timer) -> Move:
        """Randomly select a move from the available legal moves.

        Parameters
        ----------
        game : An Instance of `isolation.Board` encoding the current state of the game

        legal_moves : All legal moves encoded as pairs of int defining the next (row, col) for the agent to occupy.

        time_left : A function that returns the number of milliseconds left in the current turn.

        Returns
        ----------
        A randomly selected legal move or (-1, -1) if there are no available legal moves.
        """
        if not legal_moves:
            return -1, -1

        return choice(legal_moves)


class GreedyPlayer:
    """
    Player that chooses next move to maximize heuristic score.
    This is equivalent to a minimax search agent with a search depth of one.
    """

    def __init__(self, score_fn: Score_Function = open_move_score):
        self.score = score_fn

    # noinspection PyUnusedLocal
    def get_move(self, game: Board, legal_moves: List[Move], time_left: Timer) -> Move:
        """
        Select the move from the available legal moves with the highest heuristic score.

        Parameters
        ----------
        game : An Instance of `isolation.Board` encoding the current state of the game

        legal_moves : All legal moves encoded as pairs of int defining the next (row, col) for the agent to occupy.

        time_left : A function that returns the number of milliseconds left in the current turn.

        Returns
        ----------
        The move in the legal moves list with the highest heuristic score for the current game state.
        (-1, -1) if there are no legal moves.
        """
        if not legal_moves:
            return -1, -1

        _, move = max([(self.score(game.forecast_move(m), self), m) for m in legal_moves])
        return move


class HumanPlayer:
    """Player that chooses a move according to user's input."""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get_move(self, game: Board, legal_moves: List[Move], time_left: Timer) -> Move:
        """
        Select a move from the available legal moves based on user input at the terminal.

        Parameters
        ----------
        game : An Instance of `isolation.Board` encoding the current state of the game

        legal_moves : All legal moves encoded as pairs of int defining the next (row, col) for the agent to occupy.

        time_left : A function that returns the number of milliseconds left in the current turn.

        Returns
        ----------
        The move in the legal moves list selected by the user through the terminal prompt.
        Automatically return (-1, -1) if there are no legal moves
        """
        if not legal_moves:
            return -1, -1

        print(game.to_string())
        print((' '.join(['[{}] {}{}'.format(i, chr(ord('A') + c), r + 1) for i, (r, c) in enumerate(legal_moves)])))

        valid_choice = False
        index = 0
        while not valid_choice:
            try:
                index = int(input('Choose move index:'))
                valid_choice = 0 <= index < len(legal_moves)

                if not valid_choice:
                    print('Illegal move! Try again.')

            except ValueError:
                print('Invalid index! Try again.')

        return legal_moves[index]

    @property
    def is_time_limited(self) -> bool:
        return False
