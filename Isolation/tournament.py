"""
Estimate the strength rating of student-agent with iterative deepening and
a custom heuristic evaluation function against fixed-depth minimax and
alpha-beta search agents by running a round-robin tournament for the student
agent. Note that all agents are constructed from the student CustomPlayer
implementation, so any errors present in that class will affect the outcome
here.

The student agent plays a fixed number of "fair" matches against each test
agent. The matches are fair because the board is initialized randomly for both
players, and the players play each match twice -- switching the player order
between games. This helps to correct for imbalances in the game due to both
starting position and initiative.

For example, if the random moves chosen for initialization are (5, 2) and
(1, 3), then the first match will place agentA at (5, 2) as player 1 and
agentB at (1, 3) as player 2 then play to conclusion; the agents swap
initiative in the second match with agentB at (5, 2) as player 1 and agentA at
(1, 3) as player 2.
"""

from random import sample
from collections import namedtuple
from typing import Tuple, List

from heuristics import null_score, improved_score
from heuristics import open_move_score
from isolation import Player, Board, Location
from game_agent import CustomPlayer
from sample_players import RandomPlayer


NUM_MATCHES = 50  # number of matches against each opponent
TIME_LIMIT = 50  # number of milliseconds before timeout
TIME_MARGIN = 10  # number of milliseconds before timeout to start returning

DESCRIPTION = """
This script evaluates the performance of the custom heuristic function by
comparing the strength of an agent using iterative deepening (ID) search with
alpha-beta pruning against the strength rating of agents using other heuristic
functions.  The `ID_Improved` agent provides a baseline by measuring the
performance of a basic agent using Iterative Deepening and the "improved"
heuristic (from lecture) on your hardware.  The `Student` agent then measures
the performance of Iterative Deepening and the custom heuristic against the
same opponents.
"""

Agent = namedtuple("Agent", ["player", "name"])

Starting_Positions = Tuple[Location, Location]


def play_match(player_1: Player, player_2: Player, starting_positions: Starting_Positions) -> Tuple[int, int]:
    """
    Play a match (= two games, with each player starting once) between the players,
    forcing each agent to play from specified starting_positions.
    This should control for differences in outcome resulting from advantage due to starting position on the board.

    :param player_1: First player

    :param player_2: Second player

    :param starting_positions: Two coordinate pair (row, column) indicating 2 starting positions on the board.

    :return: Number of wins of each player
    """
    num_wins = {player_1: 0, player_2: 0}
    games = [Board(player_1, player_2), Board(player_2, player_1)]

    # play both games and tally the results
    for game in games:
        game.apply_move(starting_positions[0])
        game.apply_move(starting_positions[1])
        winner, _, _ = game.play(time_limit=TIME_LIMIT)
        num_wins[winner] += 1

    return num_wins[player_1], num_wins[player_2]


def bench_agent(agent: Agent, opponents: List[Agent], starting_position_list: List[Starting_Positions]) -> float:
    """
    Confront a given agent with a list of opponents, playing matches with the same starting positions for
    each confrontation.

    :param agent: An agent

    :param opponents: A list of opponents

    :param starting_position_list: A list of starting positions

    :return: The winning ratio of the agent
    """
    wins = 0.
    total = 0.

    print("\nPlaying Matches:")
    print("----------")

    for idx, opponent in enumerate(opponents):
        print("  Match {}: {!s:^11} vs {!s:^11}".format(idx + 1, agent.name, opponent.name), end=' ')

        agent_total, opponent_total = 0, 0
        for starting_positions in starting_position_list:
            agent_wins, opponent_wins = play_match(agent.player, opponent.player, starting_positions)
            agent_total += agent_wins
            opponent_total += opponent_wins

        print("\tResult: {} to {}".format(agent_total, opponent_total))

        wins += agent_total
        total += agent_total + opponent_total

    return 100. * wins / total


def main():

    heuristics = [("Null", null_score), ("Open", open_move_score), ("Improved", improved_score)]
    ab_args = {"search_depth": 5, "method": 'alphabeta', "iterative": False}
    mm_args = {"search_depth": 3, "method": 'minimax', "iterative": False}
    custom_args = {"method": 'alphabeta', 'iterative': True, 'timeout': TIME_MARGIN, 'reordering': True}

    # Create a collection of CPU agents using fixed-depth minimax, alpha beta search, or random selection.
    # The agent names encode the search method and the heuristic function.
    # For example, MM_Open is an agent using minimax search with the open moves heuristic.
    mm_agents = [Agent(CustomPlayer(score_fn=h, **mm_args), "MM_" + name) for name, h in heuristics]
    ab_agents = [Agent(CustomPlayer(score_fn=h, **ab_args), "AB_" + name) for name, h in heuristics]
    random_agents = [Agent(RandomPlayer(), "Random")]
    # ID_Improved agent is used for comparison to the performance of the submitted agent for calibration on the
    # performance across different systems; i.e., the performance of the student agent is considered relative to
    # the performance of the ID_Improved agent to account for faster or slower computers.
    test_agents = [Agent(CustomPlayer(**custom_args), "Custom"),
                   Agent(CustomPlayer(score_fn=improved_score, **custom_args), "ID_Improved")]

    # Generate a list of starting positions
    starting_position_list = []
    board = Board(RandomPlayer(), RandomPlayer())
    for _ in range(NUM_MATCHES):
        starting_position_list.append(tuple(sample(board.get_legal_moves(), 2)))

    for agent in test_agents:
        print("")
        print("*************************")
        print("{:^25}".format("Evaluating: " + agent.name))
        print("*************************")

        opponents = random_agents + mm_agents + ab_agents
        win_ratio = bench_agent(agent, opponents, starting_position_list)

        print("\n\nResults:")
        print("----------")
        print("{!s:<15}{:>10.2f}%".format(agent.name, win_ratio))
        print('average depth = {}'.format(agent.player.get_average_depth()))

if __name__ == "__main__":
    main()
