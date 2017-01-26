from itertools import combinations

assignments = []


def assign_value(sudoku, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    sudoku[box] = value
    if len(value) == 1:
        assignments.append(sudoku.copy())
    return sudoku


rows = 'ABCDEFGHI'
cols = '123456789'
digits = '123456789'


def cross(a, b):
    return [s + t for s in a for t in b]


boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [[s + t for s, t in zip(rows, cols)], [s + t for s, t in zip(rows, reversed(cols))]]
unit_list = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - {s}) for s in boxes)


def display(sudoku):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(sudoku[box]) for box in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in rows:
        print(''.join(sudoku[row + col].center(width) + ('|' if col in '36' else '')
                      for col in cols))
        if row in 'CF':
            print(line)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert (len(grid) == 81)
    return dict(zip(boxes, ['123456789' if v == '.' else v for v in grid]))


def eliminate(sudoku):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values
    of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for solved_box in [box for box in sudoku.keys() if len(sudoku[box]) == 1]:
        for peer in peers[solved_box]:
            assign_value(sudoku, peer, sudoku[peer].replace(sudoku[solved_box], ''))

    return sudoku


def naked_twins(sudoku):
    """
    Eliminate values using the naked twins strategy.
    Args:
        sudoku(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    for unit in unit_list:
        bivalent_boxes = [box for box in unit if len(sudoku[box]) == 2]
        twin_boxes = [(box1, box2) for (box1, box2) in combinations(bivalent_boxes, 2) if sudoku[box1] == sudoku[box2]]
        # Eliminate the naked twins as possibilities for their peers
        for box1, box2 in twin_boxes:
            digit1, digit2 = sudoku[box1]
            for peer in set(unit) - {box1, box2}:
                assign_value(sudoku, peer, sudoku[peer].replace(digit1, '').replace(digit2, ''))

    return sudoku


def only_choice(sudoku):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box,
    assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unit_list:
        for digit in digits:
            candidates = [box for box in unit if digit in sudoku[box]]
            if len(candidates) == 1:
                assign_value(sudoku, candidates[0], digit)

    return sudoku


def reduce_puzzle(sudoku):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        solved_values_before = len([box for box, values in sudoku.items() if len(values) == 1])
        sudoku = eliminate(sudoku)
        sudoku = naked_twins(sudoku)
        sudoku = only_choice(sudoku)
        solved_values_after = len([box for box in sudoku.keys() if len(sudoku[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = (solved_values_before == solved_values_after)
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in sudoku.keys() if len(sudoku[box]) == 0]):
            return False

    return sudoku


def search(sudoku):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form, or False if there is not solution
    """
    sudoku = reduce_puzzle(sudoku)
    if not sudoku:  # No solution
        return False

    unfilled_boxes = [box for box in boxes if len(sudoku[box]) > 1]
    if len(unfilled_boxes) == 0:  # Solved
        return sudoku

    # Choose one of the unfilled boxes with the fewest possibilities
    _, chosen_box = min(len(sudoku[unfilled_box]) for unfilled_box in unfilled_boxes)

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False),
    # return that answer!
    for digit in sudoku[chosen_box]:
        new_sudoku = sudoku.copy()
        assign_value(new_sudoku, chosen_box, digit)
        solution = search(new_sudoku)
        if solution:
            return solution


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
