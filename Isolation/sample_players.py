from isolation import Player, Board, Timer, Location
from random import sample


class RandomPlayer(Player):
    """Player that chooses a move randomly."""

    def get_move(self, board: 'Board', time_left: Timer) -> Location:
        """
        Randomly select a move from the available legal moves.

        :param board: The current state of the game

        :param time_left: A function that returns the number of milliseconds left in the current turn.
                          Returning with any less than 0 ms remaining forfeits the game.

        :return: A randomly selected legal move or (-1, -1) if there are no available legal moves.
        """
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return -1, -1

        return sample(legal_moves, 1)[0]


class HumanPlayer(Player):
    """Player that chooses a move according to user's input."""

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get_move(self, board: 'Board', time_left: Timer) -> Location:
        """
        Select a move from the available legal moves based on user input at the terminal.

        :param board: The current state of the game

        :param time_left: A function that returns the number of milliseconds left in the current turn.
                          Returning with any less than 0 ms remaining forfeits the game.

        :return: The legal move selected by the user through the terminal prompt or (-1, -1) if there are none.
        """
        legal_moves = list(board.get_legal_moves())
        if not legal_moves:
            return -1, -1

        legal_moves.sort()
        print(board.to_string())
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
