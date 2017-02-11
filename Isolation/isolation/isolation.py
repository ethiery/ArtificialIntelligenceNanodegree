from timeit import default_timer
from typing import Tuple, List, Callable, Union, Dict, Set
from abc import ABCMeta, abstractmethod

from copy import deepcopy

Location = Tuple[int, int]
Timer = Callable[[], float]
Board_Key = Tuple[int, Union[Location, None], Union[Location, None], bool]


class Player(object, metaclass=ABCMeta):

    @abstractmethod
    def get_move(self, board: 'Board', time_left: Timer) -> Location:
        """
        Search for the best move from the available legal moves and return a result before the time limit expires.
        Must perform iterative deepening if self.iterative=True,
        Must use the search method (minimax or alphabeta) corresponding to the self.method value.

        :param board: The current state of the game

        :param time_left: A function that returns the number of milliseconds left in the current turn.
                          Returning with any less than 0 ms remaining forfeits the game.

        :return: Board coordinates of a legal move, or (-1, -1) if there are none.
        """
        pass

    @property
    def is_time_limited(self) -> bool:
        """
        :return: True if the player has a time limit, False else (for human players)
        """
        return True


class Board(object):
    """Implement a model for the game Isolation assuming each player moves like a knight in chess."""

    BLANK = 0
    NOT_MOVED = None
    DIRECTIONS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    def __init__(self, player_1: Player, player_2: Player, width: int = 7, height: int = 7):
        """
        :param player_1: The first player (playing first).
        :param player_2: The second player (playing in second).
        :param width:    The number of columns of the board.
        :param height:   The number of rows of the board.
        """
        self.width = width
        self.height = height
        self.move_count = 0
        self.player_1 = player_1
        self.player_2 = player_2
        self.active_player = player_1
        self.inactive_player = player_2
        self.blank_spaces = {(i, j) for j in range(self.width) for i in range(self.height)}
        self.blank_spaces_int = 0
        self.locations = {player_1: Board.NOT_MOVED, player_2: Board.NOT_MOVED}

    def get_key(self) -> Board_Key:
        """
        The key of a board is defined as the uniquely identified by a tuple containing:
        - An int whose (r*width+c)-th bit is equal to 0 if cell (r,c) is still available, 1 else
        - the position of the first player
        - the position of the second player
        - a boolean indicating if the first player is active or not

        :return: The key of the board
        """
        return (self.blank_spaces_int,
                self.locations[self.player_1],
                self.locations[self.player_2],
                self.player_1 == self.active_player)

    def get_opponent(self, player: Player) -> Player:
        """
        :param player: A player registered in the current game. Raises an error if it is not.
        :return: The opponent of the input player.
        """
        if player == self.active_player:
            return self.inactive_player
        elif player == self.inactive_player:
            return self.active_player
        raise RuntimeError("`player` must be an object registered as a player in the current game.")

    def copy(self) -> 'Board':
        """
        :return: A deep copy of the current board.
        """
        new_board = Board(self.player_1, self.player_2, width=self.width, height=self.height)
        new_board.move_count = self.move_count
        new_board.active_player = self.active_player
        new_board.inactive_player = self.inactive_player
        new_board.locations = {key: val for key, val in self.locations.items()}
        new_board.blank_spaces = deepcopy(self.blank_spaces)
        new_board.blank_spaces_int = self.blank_spaces_int
        return new_board

    def forecast_move(self, move: Location) -> 'Board':
        """
        Make a deep copy of the current game with an input move applied to advance the game one ply.

        Parameters
        ----------
        move : A coordinate pair (row, column) indicating the next position for the active player on the board.

        Returns
        ----------
        A deep copy of the board with the input move applied.
        """
        new_board = self.copy()
        new_board.apply_move(move)
        return new_board

    def forecast_key(self, move: Location) -> Board_Key:
        """
        :param move: A coordinate pair (row, column) indicating the next position for the active player on the board.
        :return: The key of the board that would be obtained by applying the input move to advance the game one ply
        """
        row, col = move
        new_blank_spaces_int = self.blank_spaces_int + (1 << (row * self.width + col))
        if self.player_1 == self.active_player:
            return new_blank_spaces_int, move, self.locations[self.player_2], False
        else:
            return new_blank_spaces_int, self.locations[self.player_1], move, True

    def get_player_location(self, player: Player) -> Location:
        """
        :param player: One of the registered player of the current game.

        :return: The the location of the input player on the board, as a coordinate pair (row, column)
        """
        # return self.history[player][-1]
        return self.locations[player]

    def get_legal_moves(self, player: Player = None) -> Set[Location]:
        """
        :param player: One of the registered player of the current game. Defaults to the active player.

        :return: A set of all the legal moves for the input player, as coordinate pairs (row, column)
        """
        if player is None:
            player = self.active_player

        location = self.locations[player]
        if location == Board.NOT_MOVED:
            return set(self.blank_spaces)

        r, c = location
        return {(r + dr, c + dc) for dr, dc in Board.DIRECTIONS} & self.blank_spaces

    def get_reachable_locations(self, player: Player) -> Dict[int, Set[Location]]:
        """
        :param player: One of the registered player of the current game
        :return: Dictionary in which reachable locations are sorted by the number of moves required to reach them
        """
        # If no cell is reachable, return an empty dictionary directly
        directly_reachable = set(self.get_legal_moves(player))
        if len(directly_reachable) == 0:
            return dict()

        # Perform a BFS to find all reachable cells, keeping track of the number of moves required to do so
        reachable_by_depth = {1: directly_reachable}
        not_reached_yet = self.blank_spaces - directly_reachable
        d = 1
        while d in reachable_by_depth:
            # find cells reachable from cells reachable in exactly d moves
            just_reached = set()
            for r, c in reachable_by_depth[d]:
                just_reached.update({(r + dr, c + dc) for dr, dc in Board.DIRECTIONS})
            # obtain cells reachable in exactly d+1 moves by excluding cells that were reachable in less moves
            just_reached.intersection_update(not_reached_yet)
            # update the set of unreached cells, and the result dictionary
            if len(just_reached) > 0:
                not_reached_yet -= just_reached
                reachable_by_depth[d + 1] = just_reached
            d += 1

        return reachable_by_depth

    def apply_move(self, move: Location):
        """
        Move the active player to a specified location.

        :param move: Coordinate pair (row, column) indicating the next position for the active player on the board
        """
        row, col = move
        self.locations[self.active_player] = move
        self.blank_spaces.remove(move)
        self.blank_spaces_int += (1 << (row * self.width + col))
        self.active_player, self.inactive_player = self.inactive_player, self.active_player
        self.move_count += 1

    def utility(self, player: Union[Player, None] = None) -> float:
        """
        :param player: One of the registered player of the current game. Defaults to the active player.

        :return: The utility value of the current game state for the specified player, which is +inf if the player wins,
                 -inf if he loses, and 0 otherwise.
        """
        if not self.get_legal_moves(self.active_player):
            if player == self.inactive_player:
                return float("inf")
            if player == self.active_player:
                return float("-inf")

        return 0.

    def to_string(self) -> str:
        """
        :return: A string representation of the current game state, marking the location of each player and indicating
                 which cells have been blocked, and which remain open.
        """
        symbol = {(i, j): ' ' if (i, j) in self.blank_spaces else '-'
                  for i in range(self.height) for j in range(self.width)}

        symbol[self.locations[self.player_1]] = '1'
        symbol[self.locations[self.player_2]] = '2'

        horizontal_line = '-' * (4 * self.width + 3) + '\n\r'

        out = '  | {}\n\r'.format(' | '.join([chr(ord('A') + i) for i in range(self.width)]))
        out += horizontal_line
        for i in range(self.height):
            out += '{} | {}'.format(i + 1, ' | '.join([symbol[(i, j)] for j in range(self.width)]) + '\n\r')
            out += horizontal_line

        return out

    @staticmethod
    def make_timer(time_limit: float) -> Callable[[], float]:
        """
        :param time_limit: The maximal duration of the current turn in milliseconds
        :return:           A function that returns the number of milliseconds left in the current turn.
        """
        starting_time = default_timer()

        def timer() -> float:
            return time_limit - 1000 * (default_timer() - starting_time)

        return timer

    def play(self, time_limit: float = 200) -> Tuple[Player, List[Location], str]:
        """
        Execute a match between the players by alternately soliciting them to select a move and applying it in the game.

        :param time_limit: (Optional) The number of ms to allow before timeout during each turn. Defaults to 200 ms.

        :return: the winning player, the complete game history and a string indicating the reason for losing
                 ('timeout' or 'invalid move').
        """
        history = []
        while True:
            game_copy = self.copy()
            time_left = Board.make_timer(time_limit)
            move = self.active_player.get_move(game_copy, time_left)
            remaining = time_left()

            if remaining < 0 and self.active_player.is_time_limited:
                reason = 'timeout'
                break

            if move not in self.get_legal_moves():
                reason = 'illegal move'
                break

            self.apply_move(move)
            history.append(move)

        return self.inactive_player, history, reason
