import timeit
from typing import Tuple, List, Callable, Union
from abc import ABCMeta, abstractmethod

from copy import deepcopy
from copy import copy

Move = Tuple[int, int]
Timer = Callable[[], float]
Board_Key = Tuple[int, Move, Move, bool]


class Player(object, metaclass=ABCMeta):

    @abstractmethod
    def get_move(self, game: 'Board', legal_moves: List[Move], time_left: Timer) -> Move:
        """
        Search for the best move from the available legal moves and return a result before the time limit expires.
        Must perform iterative deepening if self.iterative=True,
        Must use the search method (minimax or alphabeta) corresponding to the self.method value.

        Parameters
        ----------
        game : An Instance of `isolation.Board` encoding the current state of the game

        legal_moves : All legal moves encoded as pairs of int defining the next (row, col) for the agent to occupy.

        time_left : A function that returns the number of milliseconds left in the current turn.
                    Returning with any less than 0 ms remaining forfeits the game.

        Returns
        -------
        Board coordinates corresponding to a legal move; possibly (-1, -1) if there are no available legal moves.
        """
        pass

    @property
    def is_time_limited(self) -> bool:
        return True


class Board(object):
    """Implement a model for the game Isolation assuming each player moves like a knight in chess."""

    BLANK = 0
    NOT_MOVED = None
    DIRECTIONS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    def __init__(self, player_1: Player, player_2: Player, width: int = 7, height: int = 7):
        """
        Parameters
        ----------
        player_1 : An instance of `isolation.Player` whose `get_move()` function define the first player behaviour

        player_2 : An instance of `isolation.Player` whose `get_move()` function define the second player behaviour

        width : The number of columns that the board should have.

        height : The number of rows that the board should have.
        """
        self.width = width
        self.height = height
        self.move_count = 0
        self.__player_1__ = player_1
        self.__player_2__ = player_2
        self.__active_player__ = player_1
        self.__inactive_player__ = player_2
        self.__blank_spaces__ = {(i, j) for j in range(self.width) for i in range(self.height)}
        self.__blank_spaces_int__ = 0
        self.__last_player_move__ = {player_1: Board.NOT_MOVED, player_2: Board.NOT_MOVED}

    def get_key(self) -> Board_Key:
        """
        A board is uniquely identied by a tuple containing:
        - An int whose (r*width+c)-th bit is equal to 0 if cell (r,c) is still available, 1 else
        - the position of the first player
        - the position of the second player
        - a boolean indicating if the first player is active or not
        """
        return (self.__blank_spaces_int__,
                self.__last_player_move__[self.__player_1__],
                self.__last_player_move__[self.__player_2__],
                self.__player_1__ == self.__active_player__)

    @property
    def active_player(self) -> Player:
        """The Player registered as holding initiative in the current game state."""
        return self.__active_player__

    @property
    def inactive_player(self) -> Player:
        """The Player registered as in waiting for the current game state."""
        return self.__inactive_player__

    def get_opponent(self, player: Player) -> Player:
        """
        Return the opponent of the supplied player.

        Parameters
        ----------
        player : A player registered in the current game. Raises an error if it is not.

        Returns
        ----------
        The opponent of the input player.
        """
        if player == self.__active_player__:
            return self.__inactive_player__
        elif player == self.__inactive_player__:
            return self.__active_player__
        raise RuntimeError("`player` must be an object registered as a player in the current game.")

    def copy(self) -> 'Board':
        """
        Make a deep copy of the current board.

        Returns
        ----------
        A deep copy of the current board.
        """
        new_board = Board(self.__player_1__, self.__player_2__, width=self.width, height=self.height)
        new_board.move_count = self.move_count
        new_board.__active_player__ = self.__active_player__
        new_board.__inactive_player__ = self.__inactive_player__
        new_board.__last_player_move__ = copy(self.__last_player_move__)
        new_board.__blank_spaces__ = deepcopy(self.__blank_spaces__)
        new_board.__blank_spaces_int__ = self.__blank_spaces_int__
        return new_board

    def forecast_move(self, move: Move) -> 'Board':
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

    def get_forecast_key(self, move: Move) -> Board_Key:
        """
        Compute the key of the board obtained by applying an input move the advance the game one ply,
        without actually doing it.

        Parameters
        ----------
        move : A coordinate pair (row, column) indicating the next position for the active player on the board.

        Returns
        ----------
        A key of the board with the input move applied.
        """
        row, col = move
        new_blank_spaces_int = self.__blank_spaces_int__ + (1 << (row * self.width + col))
        if self.__player_1__ == self.__active_player__:
            return new_blank_spaces_int, move, self.__last_player_move__[self.__player_2__], False
        else:
            return new_blank_spaces_int, self.__last_player_move__[self.__player_1__], move, True

    def get_blank_spaces(self) -> List[Move]:
        """
        Return a list of the locations that are still available on the board.
        """
        return list(self.__blank_spaces__)

    def get_player_location(self, player: Player) -> Move:
        """
        Find the current location of the specified player on the board.

        Parameters
        ----------
        player : One of the registered player of the current game.

        Returns
        ----------
        The coordinate pair (row, column) of the input player.
        """
        return self.__last_player_move__[player]

    def get_legal_moves(self, player: Player = None) -> List[Move]:
        """
        Return the list of all legal moves for the specified player.

        Parameters
        ----------
        player : One of the registered player of the current game (optional).
                 If None, the active player will be considered.

        Returns
        ----------
        The list of coordinate pairs (row, column) of all legal moves for the player in the current game state.
        """
        if player is None:
            player = self.active_player

        move = self.__last_player_move__[player]
        if move == Board.NOT_MOVED:
            return self.get_blank_spaces()

        r, c = move
        return list({(r + dr, c + dc) for dr, dc in Board.DIRECTIONS} & self.__blank_spaces__)

    def apply_move(self, move: Move):
        """
        Move the active player to a specified location.

        Parameters
        ----------
        move : Coordinate pair (row, column) indicating the next position for the active player on the board.
        """
        row, col = move
        self.__last_player_move__[self.active_player] = move
        self.__blank_spaces__.remove(move)
        self.__blank_spaces_int__ += (1 << (row * self.width + col))
        self.__active_player__, self.__inactive_player__ = self.__inactive_player__, self.__active_player__
        self.move_count += 1

    def utility(self, player: Union[Player, None] = None) -> float:
        """
        Returns the utility of the current game state from the perspective of the specified player.
        Which is +inf if he wins, -inf if he loses, and 0 otherwise

        Parameters
        ----------
        player : One of the registered player of the current game (optional).
                 If None, the active player is considered.

        Returns
        ----------
        The utility value of the current game state for the specified player, which is +inf if the player wins,
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
        Generate a string representation of the current game state, marking
        the location of each player and indicating which cells have been
        blocked, and which remain open.
        """

        p1_loc = self.__last_player_move__[self.__player_1__]
        p2_loc = self.__last_player_move__[self.__player_2__]

        # Column labels
        out = '  | '
        for i in range(self.width):
            out += '{} | '.format(chr(ord('A') + i))
        out += '\n\r--{}\n\r'.format('-' * (4 * self.width + 1))

        # Rows
        for i in range(self.height):
            out += '{} | '.format(i + 1)

            for j in range(self.width):
                if (i, j) in self.__blank_spaces__:
                    out += ' '
                elif p1_loc and p1_loc == (i, j):
                    out += '1'
                elif p2_loc and p2_loc == (i, j):
                    out += '2'
                else:
                    out += '-'

                out += ' | '
            out += '\n\r--{}\n\r'.format('-' * (4 * self.width + 1))

        return out

    @staticmethod
    def curr_time_millis() -> float:
        """Returns current time in milliseconds"""
        return 1000 * timeit.default_timer()

    def play(self, time_limit: float = 200) -> Tuple[Player, List, str]:
        """
        Execute a match between the players by alternately soliciting them to select a move and applying it in the game.

        Parameters
        ----------
        time_limit : The maximum number of ms to allow before timeout during each turn. Optional, defaults to 200 ms.

        Returns
        ----------
        the winning player,
        the complete game move history,
        a string indicating the reason for losing (e.g., timeout or invalid move).
        """
        move_history = []

        while True:
            legal_player_moves = self.get_legal_moves()
            game_copy = self.copy()
            move_start = self.curr_time_millis()
            time_left = lambda: time_limit - (self.curr_time_millis() - move_start)
            curr_move = self.active_player.get_move(game_copy, legal_player_moves, time_left)
            move_end = time_left()

            if curr_move is None:
                curr_move = Board.NOT_MOVED

            if self.active_player == self.__player_1__:
                move_history.append([curr_move])
            else:
                move_history[-1].append(curr_move)

            if self.active_player.is_time_limited and move_end < 0:
                return self.__inactive_player__, move_history, "timeout"

            if curr_move not in legal_player_moves:
                return self.__inactive_player__, move_history, "illegal move"

            self.apply_move(curr_move)
