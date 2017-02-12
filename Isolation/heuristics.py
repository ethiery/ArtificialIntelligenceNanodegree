from typing import Callable
from random import choice

from isolation import Player, Board

Score_Function = Callable[[Board, Player], float]


def null_score(board: Board, player: Player) -> float:
    """
    This heuristic presumes no knowledge for non-terminal states, and
    returns the same uninformative value for all other states.

    :param board: The current state of the game

    :param player: One of the registered player of the current game

    :return: The heuristic value of the input game state for the input player.
    """
    return board.utility(player)


def open_move_score(board: Board, player: Player) -> float:
    """
    This heuristic returns a score equal to the number of moves open for a given player on the board.

    :param board: The current state of the game

    :param player: One of the registered player of the current game

    :return: The heuristic value of the input game state for the input player.
    """
    return float(len(board.get_legal_moves(player)))


def improved_score(board: Board, player: Player):
    """
    This heuristic outputs a score equal to the difference in the number of moves available to the two players.

    :param board: The current state of the game

    :param player: One of the registered player of the current game

    :return: The heuristic value of the input game state for the input player.
    """
    own_moves = len(board.get_legal_moves(player))
    opp_moves = len(board.get_legal_moves(board.get_opponent(player)))
    return float(own_moves - opp_moves)


def pure_monte_carlo_score(board: Board, player: Player, nb_rollouts=5) -> float:
    """
    This heuristic outputs the average outcome over a given number of random rollouts.

    :param board: The current state of the game

    :param player: One of the registered player of the current game

    :param nb_rollouts: Number of rollouts to average on.

    :return: The heuristic value of the input game state for the input player.
    """
    average_outcome = 0.0

    for _ in range(nb_rollouts):
        # Simulate a random game on a copy of the board
        copy = board.copy()
        legal_moves = copy.get_legal_moves()
        while legal_moves:
            copy.apply_move(choice(legal_moves))
            legal_moves = copy.get_legal_moves()

        # Outcome is 1 for a win, -1 for a lose
        average_outcome += 1.0 if copy.active_player != player else -1.0

    average_outcome /= nb_rollouts

    return average_outcome


def reach_score(board: Board, player: Player, common_ratio: float = 1.3) -> float:
    """
    This heuristic outputs the reach score of a game state for a given player, which is defined as the sum over
    all cells of the board of:
     - 0 if the cell is no longer reachable by the player
     - common_ratio^(1 - k) else, where k is the minimal number of moves to reach the cell
     ( 1 for cells reachable in 1 move, 1/common_ratio for cells reachable in 2 moves, etc)

    :param board: The current state of the game

    :param player: One of the registered player of the current game

    :param common_ratio: common ratio of the geometric progression used to weight reachable cells

    :return: The heuristic value of the input game state for the input player.
    """
    reachable = board.get_reachable_locations(player)
    return float(sum([len(cells) * pow(common_ratio, 1 - depth) for depth, cells in reachable.items()]))


def differential_reach_score(board: Board, player: Player, common_ratio: float = 1.4) -> float:
    """
    This heuristic outputs the differential reach score of a game state for a given player, which is defined as
    the reach score of this game state for this player minus the reach score of this game state for his opponent.

    :param board: The current state of the game

    :param player: One of the registered player of the current game

    :param common_ratio: common ratio of the geometric progression used to weight reachable cells

    :return: The heuristic value of the input game state for the input player.
    """
    return reach_score(board, player, common_ratio) - reach_score(board, board.get_opponent(player), common_ratio)
