from operator import itemgetter
from math import pow

"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def reachability_score(game, player):
    """
    We define the reachability score of a game state for a given player as the sum of
    the reachability score of each cell for this player.

    We define the reachability score of a cell for a given player as
     - 0 if the cell is no longer reachable by the player
     - 2^(1-k) else, where k is the minimal number of moves to reach the cell
       (1 for cells reachable in 1 move, 0.5 for cells reachable in 2 moves, etc)

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The reachability score of the current game state for the specified player.
    """
    score = 0
    blanks = set(game.get_blank_spaces())
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    # Perform a BFS, keeping track of the depth, and adding cell values to the score as we go along
    queue = [(0, game.get_player_location(player))]
    while len(queue) > 0:
        depth, (r, c) = queue.pop(0)
        valid_moves = {(r + dr, c + dc) for dr, dc in directions} & blanks
        score += len(valid_moves) * pow(2, -depth)
        blanks.difference_update(valid_moves)
        queue.extend([(depth + 1, move) for move in valid_moves])

    return float(score)


def differential_reachability_score(game, player):
    """
    We define the differential reachability score of a game state for a given player as
    the reachability score of this game state for this player minus the reachability score
    of this game state for the opponent.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The differential reachability score of the current game state for the specified player.
    """
    return float(reachability_score(game, player) - reachability_score(game, game.get_opponent(player)))


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    return differential_reachability_score(game, player)


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function performs iterative deepening if self.iterative=True,
        and it uses the search method (minimax or alphabeta) corresponding
        to the self.method value.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Return immediately if there is no legal move
        if len(legal_moves) == 0:
            return -1, -1

        # Initialize the search method function (minimax or alphabeta)
        method_fn = self.alphabeta if self.method == 'alphabeta' else self.minimax

        # If the search method times out before a first move is found, and arbitrary move is chosen
        best = self.score(game.forecast_move(legal_moves[0]), self), legal_moves[0]

        # The search method raises an exception when getting close to timeout
        # We thus call it in a try/except block
        try:
            if self.iterative:
                depth = 1
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

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch from the player's perspective

        tuple(int, int)
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

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        -------
        float
            The score for the current search branch

        tuple(int, int)
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
