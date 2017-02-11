from operator import itemgetter
from typing import Tuple
from heuristics import Score_Function, differential_reach_score

from isolation import Board, Player, Location, Timer


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


custom_score = differential_reach_score


class CustomPlayer(Player):
    """
    Game-playing agent that chooses a move using a custom evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning.
    """

    def __init__(self, search_depth: int = 3, score_fn: Score_Function = differential_reach_score,
                 iterative: bool = True, method: str = 'minimax', timeout: float = 10., reordering: bool = False):
        """

        :param search_depth: A strictly positive integer for the number of layers in the game tree to explore
                             for fixed-depth search.

        :param score_fn:     A function to use for heuristic evaluation of game states.

        :param iterative:    Whether to perform fixed-depth search (False) or iterative deepening search (True).

        :param method:       The name of the search method to use in {'minimax', 'alphabeta'}

        :param timeout:      Time remaining (in milliseconds) when search is aborted. Should be a positive value large
                             enough to allow the function to return before the timer expires.

        :param reordering: Set to True to reorder branches of the game tree using knowledge of previous iterations
        """
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.reordering = reordering
        self.cache = dict()
        self.move_count = 0
        self.total_move_count = 0
        self.average_depth = 0

    def get_move(self, board: Board, time_left: Timer) -> Location:
        """
        Search for the best move from the available legal moves and return a result before the time limit expires.
        Must perform iterative deepening if self.iterative=True,
        Must use the search method (minimax or alphabeta) corresponding to the self.method value.

        :param board: The current state of the game

        :param time_left: A function that returns the number of milliseconds left in the current turn.
                          Returning with any less than 0 ms remaining forfeits the game.

        :return: Board coordinates of a legal move, or (-1, -1) if there are none.
        """
        self.time_left = time_left

        # Initialize the search method function (minimax or alphabeta)
        method_fn = self.alphabeta if self.method == 'alphabeta' else self.minimax

        # Reset the cache when starting a new game
        if board.move_count < self.total_move_count:
            self.cache = dict()
        self.total_move_count = board.move_count

        # The search methods raise an exception when getting close to timeout
        # Hence why they are called in a try/except block
        best = float('-inf'), (-1, -1)
        try:
            if self.iterative:
                nb_cells_left = board.width * board.height - board.move_count
                for depth in range(1, nb_cells_left + 1):
                    value, move = method_fn(board, depth, maximizing_player=True)
                    best = max(best, (value, move), key=itemgetter(0))
                    if value == float('+inf'):
                        break
                    self.average_depth += 1
            else:
                best = method_fn(board, self.search_depth, True)

        except Timeout:
            self.move_count += 1
            pass

        return best[1]

    def get_average_depth(self):
        average_depth = self.average_depth / self.move_count
        self.average_depth = self.move_count = 0
        return average_depth

    def minimax(self, board: Board, depth: int, maximizing_player: bool = True) -> Tuple[float, Location]:
        """
        Implement the minimax search algorithm

        :param board: The current state of the game

        :param depth: The maximum number of plies to search in the game tree before aborting

        :param maximizing_player: Must be True if the current search depth corresponds to a max layer, False else

        :return: The best score and move for the current search branch from the player's perspective, or
                 (-1, -1) if there is no legal move available
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # The value of a leaf of the game tree is its utility value from the player's perspective
        state_utility = board.utility(self)
        if state_utility != 0:
            result = state_utility, (-1, -1)

        # At depth 0, the recursion stops and the evaluation function is called
        elif depth <= 0:
            result = self.score(board, self), (-1, -1)

        # For greater depth, the children state values are computed in order to get the backed-up value of the state
        else:
            comparison_fn = max if maximizing_player else min
            result = float('-inf' if maximizing_player else 'inf'), (-1, -1)

            for move in board.get_legal_moves():
                value = self.minimax(board.forecast_move(move), depth - 1, not maximizing_player)[0]
                result = comparison_fn(result, (value, move), key=itemgetter(0))

        return result

    def alphabeta(self, board: Board, depth: int, alpha: float = float("-inf"), beta: float = float("inf"),
                  maximizing_player: bool = True) -> Tuple[float, Location]:
        """
        Implement the minimax search algorithm with alpha-beta pruning

        :param board: The current state of the game

        :param depth: The maximum number of plies to search in the game tree before aborting

        :param alpha: The lower bound of search on minimizing layers

        :param beta: The upper bound of search on maximizing layers

        :param maximizing_player: Must be True if the current search depth corresponds to a max layer, False else

        :return: The best score and move for the current search branch from the player's perspective, or
                 (-1, -1) if there is no legal move available
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # The value of a leaf of the game tree is its utility value from the player's perspective
        state_utility = board.utility(self)
        if state_utility != 0:
            result = state_utility, (-1, -1)

        # At depth 0, the recursion stops and the evaluation function is called
        elif depth <= 0:
            result = self.score(board, self), (-1, -1)

        # Else, the children state values are computed in order to get the backed-up value of the state
        elif maximizing_player:
            result = float('-inf'), (-1, -1)
            moves = list(board.get_legal_moves())
            # If reordering is enable, possible moves are explored by decreasing cached value to maximize pruning
            if self.reordering:
                moves.sort(key=lambda m: self.cache.get(board.forecast_key(m), float('-inf')), reverse=True)

            for move in moves:
                value = self.alphabeta(board.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                result = max(result, (value, move), key=itemgetter(0))
                if value >= beta:
                    break
                alpha = max(alpha, value)

        else:
            result = float('inf'), (-1, -1)
            moves = list(board.get_legal_moves())
            # If reordering is enable, possible moves are explored by increased cached value to maximize pruning
            if self.reordering:
                moves.sort(key=lambda m: self.cache.get(board.forecast_key(m), float('+inf')), reverse=False)

            for move in moves:
                value = self.alphabeta(board.forecast_move(move), depth - 1, alpha, beta, not maximizing_player)[0]
                result = min(result, (value, move), key=itemgetter(0))
                if value <= alpha:
                    break
                beta = min(beta, value)

        # Cache value and return it
        self.cache[board.get_key()] = result[0]
        return result
