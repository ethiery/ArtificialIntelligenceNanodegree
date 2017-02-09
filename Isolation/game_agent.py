from operator import itemgetter
from math import pow
from typing import Dict, Set, Tuple, List

from isolation import Board, Player, Move, Timer
from sample_players import Score_Function


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def get_reachable_cells(game: Board, player: Player) -> Dict[int, Set[Move]]:
    """
    Compute which cells of a given board are reachable by a given player

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game

    player : One of the registered player of the current game

    Returns
    -------
    Dictionary of reachable cells sorted by the minimal number of moves they can be reached in
    """
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    # If no cell is reachable, return an empty dictionary directly
    directly_reachable = set(game.get_legal_moves(player))
    if len(directly_reachable) == 0:
        return dict()

    # Basically perform a BFS to find all reachable cells, keeping track of the number of moves required to do so
    reachable_by_depth = {1: directly_reachable}
    not_reached_yet = set(game.get_blank_spaces()) - directly_reachable
    d = 1
    while d in reachable_by_depth:
        # find cells reachable from cells reachable in exactly d moves
        just_reached = set()
        for r, c in reachable_by_depth[d]:
            just_reached.update({(r + dr, c + dc) for dr, dc in directions})
        # obtain cells reachable in exactly d+1 moves by excluding cells that were reachable in less moves
        just_reached.intersection_update(not_reached_yet)
        # update the set of unreached cells, and the result dictionary
        if len(just_reached) > 0:
            not_reached_yet -= just_reached
            reachable_by_depth[d + 1] = just_reached
        d += 1

    return reachable_by_depth


def reach_score(game: Board, player: Player, common_ratio: float = 1.1) -> float:
    """
    The reach score of a game state for a given player is defined as the sum over all cells of the board of:
     - 0 if the cell is no longer reachable by the player
     - common_ratio^(1 - k) else, where k is the minimal number of moves to reach the cell
     ( 1 for cells reachable in 1 move, 1/common_ratio for cells reachable in 2 moves, etc)

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game

    player : One of the registered player of the current game

    common_ratio : common ratio of the geometric progression used to weight reachable cells when computing the score

    Returns
    -------
    The reach score of the current game state for the specified player
    """
    reachable = get_reachable_cells(game, player)
    return float(sum([len(cells) * pow(common_ratio, 1 - depth) for depth, cells in reachable.items()]))


def differential_reach_score(game: Board, player: Player, common_ratio: float = 1.1) -> float:
    """
    The differential reach score of a game state for a given player is defined as
    the reach score of this game state for this player minus the reach score of this game state for his opponent.

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game

    player : One of the registered player of the current game

    common_ratio : common ratio of the geometric progression used to weight reachable cells when computing the score

    Returns
    -------
    float
        The differential reach score of the current game state for the specified player.
    """
    return reach_score(game, player, common_ratio) - reach_score(game, game.get_opponent(player), common_ratio)


def custom_score(game: Board, player: Player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : An instance of `isolation.Board` encoding the current state of the game

    player : One of the registered player of the current game

    Returns
    -------
    The heuristic value of the current game state to the specified player.
    """
    utility = game.utility(player)
    if utility != 0:
        return utility

    return differential_reach_score(game, player)


class CustomPlayer(Player):
    """
    Game-playing agent that chooses a move using a custom evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning.
    """

    def __init__(self, search_depth: int = 3, score_fn: Score_Function = custom_score, iterative: bool = True,
                 method: str = 'minimax', timeout: float = 10.):
        """
        Parameters
        ----------
        search_depth (optional): A strictly positive integer for the number of layers in the game tree to explore
                                 for fixed-depth search. (a depth of 1 would only explore the immediate sucessors of the
                                 current state.)

        score_fn (optional): A function to use for heuristic evaluation of game states.

        iterative (optional): Whether to perform fixed-depth search (False) or iterative deepening search (True).

        method (optional): The name of the search method to use in {'minimax', 'alphabeta'}

        timeout (optional): Time remaining (in milliseconds) when search is aborted. Should be a positive value large
                            enough to allow the function to return before the timer expires.
        """
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game: 'Board', legal_moves: List[Move], time_left: Timer) -> Move:
        """
        Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function performs iterative deepening if self.iterative=True,
        and it uses the search method (minimax or alphabeta) corresponding
        to the self.method value.

        Parameters
        ----------
        game : An instance of `isolation.Board` encoding the current state of the game

        legal_moves : All legal moves encoded as pairs of int defining the next (row, col) for the agent to occupy.

        time_left : A function that returns the number of milliseconds left in the current turn.
                    Returning with any less than 0 ms remaining forfeits the game.

        Returns
        -------
        Board coordinates corresponding to a legal move; possibly (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Return immediately if there is no legal move
        if len(legal_moves) == 0:
            return -1, -1

        # Initialize the search method function (minimax or alphabeta)
        method_fn = self.alphabeta if self.method == 'alphabeta' else self.minimax

        # The search methods raise an exception when getting close to timeout
        # Hence why they are called in a try/except block
        best = self.score(game.forecast_move(legal_moves[0]), self), legal_moves[0]
        depth = 1
        try:
            if self.iterative:
                while True:
                    value, move = method_fn(game, depth, True)
                    best = max(best, (value, move), key=itemgetter(0))
                    depth += 1

            else:
                best = method_fn(game, self.search_depth, True)

        except Timeout:
            pass

        # Return the best move found yet
        return best[1]

    def minimax(self, game: Board, depth: int, maximizing_player: bool = True) -> Tuple[float, Move]:
        """
        Implement the minimax search algorithm

        Parameters
        ----------
        game : An instance of `isolation.Board` encoding the current state of the game

        depth : An integer representing the maximum number of plies to search in the game tree before aborting

        maximizing_player : Whether the current search depth corresponds to a max (True) or a min layer (False)

        Returns
        -------
        The score for the current search branch from the player's perspective

        The best move for the current branch; (-1, -1) for no legal moves
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # When a leaf of the game tree is reached, the recursion ends
        # and the utility value of the current state from the player's perspective is returned
        state_utility = game.utility(self)
        if state_utility != 0:
            return state_utility, (-1, -1)

        # When depth equals 0, the recursion ends too
        # but the evaluated value of the current state from the player's perspective is returned
        if depth <= 0:
            return self.score(game, self), (-1, -1)

        # Else the children nodes are examined to determine the backed-up value of the current state.
        children_values = [(self.minimax(game.forecast_move(move), depth - 1, not maximizing_player)[0], move)
                           for move in game.get_legal_moves()]
        if maximizing_player:
            return max(children_values, key=itemgetter(0))
        else:
            return min(children_values, key=itemgetter(0))

    def alphabeta(self, game: Board, depth: int, alpha: float = float("-inf"), beta: float = float("inf"),
                  maximizing_player: bool = True):
        """
        Implement minimax search with alpha-beta pruning

        Parameters
        ----------
        game : An instance of `isolation.Board` encoding the current state of the game

        depth : An integer representing the maximum number of plies to search in the game tree before aborting

        alpha : Alpha limits the lower bound of search on minimizing layers

        beta : Beta limits the upper bound of search on maximizing layers

        maximizing_player : Whether the current search depth corresponds to a max (True) or a min layer (False)

        Returns
        -------
        The score for the current search branch from the player's perspective

        The best move for the current branch; (-1, -1) for no legal moves
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # When a leaf of the game tree is reached, the recursion ends
        # and the utility value of the current state from the player's perspective is returned
        state_utility = game.utility(self)
        if state_utility != 0:
            return state_utility, (-1, -1)

        # When depth equals 0, the recursion ends too
        # but the evaluated value of the current state from the player's perspective is returned
        if depth <= 0:
            return self.score(game, self), (-1, -1)

        # Else the children nodes are examined to determine the backed-up value of the current state.
        if maximizing_player:
            best = float('-inf'), (-1, -1)
            for move in game.get_legal_moves():
                value = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                best = max(best, (value, move), key=itemgetter(0))
                # pruning: if value is greater than beta, this branch won't be chosen by the minimax algorithm
                if value >= beta:
                    break
                alpha = max(alpha, value)
            return best

        else:
            best = float('inf'), (-1, -1)
            for move in game.get_legal_moves():
                value = self.alphabeta(game.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                best = min(best, (value, move), key=itemgetter(0))
                # pruning: if value is lower than alpha, this branch won't be chosen by the minimax algorithm
                if value <= alpha:
                    break
                beta = min(beta, value)
            return best
