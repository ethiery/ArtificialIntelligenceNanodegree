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

from warnings import warn
from random import choice
from collections import namedtuple
from typing import Tuple

from game_agent import CustomPlayer, differential_reach_score
from isolation import Player, Board
from sample_players import RandomPlayer, null_score, open_move_score, improved_score

NUM_MATCHES = 20  # number of matches against each opponent
TIME_LIMIT = 150  # number of milliseconds before timeout

TIMEOUT_WARNING = "One or more agents lost a match this round due to " + \
                  "timeout. The get_move() function must return before " + \
                  "time_left() reaches 0 ms. You will need to leave some " + \
                  "time for the function to return, and may need to " + \
                  "increase this margin to avoid timeouts during  " + \
                  "tournament play."

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


def play_match(player_1: Player, player_2: Player,
               starting_positions: Tuple[Tuple[int, int], Tuple[int, int]]) -> Tuple[int, int]:
    """
    Play a match (= two games, with each player starting once) between the players,
    forcing each agent to play from specified starting_positions.
    This should control for differences in outcome resulting from advantage due to starting position on the board.

    Parameters
    ----------
    player_1 : First player

    player_2 : Second player

    starting_positions : Two coordinate pair (row, column) indicating 2 starting positions on the board.

    Returns
    -------
    Number of wins of each player
    """
    num_wins = {player_1: 0, player_2: 0}
    games = [Board(player_1, player_2), Board(player_2, player_1)]

    # play both games and tally the results
    for game in games:
        game.apply_move(starting_positions[0])
        game.apply_move(starting_positions[1])
        winner, _, termination = game.play(time_limit=TIME_LIMIT)
        num_wins[winner] += 1

        if termination == "timeout":
            warn(TIMEOUT_WARNING)

    return num_wins[player_1], num_wins[player_2]


def play_tournament(agents, starting_position_list):
    """
    Play a tournament, that is a given number of identical matches between the last agent and each one of the other
    """
    agent_1 = agents[-1]
    wins = 0.
    total = 0.

    print("\nPlaying Matches:")
    print("----------")

    for idx, agent_2 in enumerate(agents[:-1]):
        counts = {agent_1.player: 0., agent_2.player: 0.}
        names = [agent_1.name, agent_2.name]
        print("  Match {}: {!s:^11} vs {!s:^11}".format(idx + 1, *names), end=' ')

        for starting_positions in starting_position_list:
            score_1, score_2 = play_match(agent_1.player, agent_2.player, starting_positions)
            counts[agent_1.player] += score_1
            counts[agent_2.player] += score_2
            total += score_1 + score_2

        wins += counts[agent_1.player]
        print("\tResult: {} to {}".format(int(counts[agent_1.player]), int(counts[agent_2.player])))

    return 100. * wins / total


def main():

    heuristics = [("Null", null_score), ("Open", open_move_score), ("Improved", improved_score)]
    ab_args = {"search_depth": 5, "method": 'alphabeta', "iterative": False}
    mm_args = {"search_depth": 3, "method": 'minimax', "iterative": False}
    custom_args = {"method": 'alphabeta', 'iterative': True}

    # Create a collection of CPU agents using fixed-depth minimax or alpha beta
    # search, or random selection.  The agent names encode the search method
    # (MM=minimax, AB=alpha-beta) and the heuristic function (Null=null_score,
    # Open=open_move_score, Improved=improved_score). For example, MM_Open is
    # an agent using minimax search with the open moves heuristic.
    mm_agents = [Agent(CustomPlayer(score_fn=h, **mm_args), "MM_" + name) for name, h in heuristics]
    ab_agents = [Agent(CustomPlayer(score_fn=h, **ab_args), "AB_" + name) for name, h in heuristics]
    random_agents = [Agent(RandomPlayer(), "Random")]

    # ID_Improved agent is used for comparison to the performance of the submitted agent for calibration on the
    # performance across different systems; i.e., the performance of the student agent is considered relative to
    # the performance of the ID_Improved agent to account for faster or slower computers.
    test_agents = [Agent(CustomPlayer(score_fn=differential_reach_score, **custom_args),
                         "Student, differential reach score"),
                   Agent(CustomPlayer(score_fn=improved_score, **custom_args), "ID_Improved")]

    starting_position_list = []
    for _ in range(NUM_MATCHES):
        board = Board(RandomPlayer(), RandomPlayer())
        ply1 = choice(board.get_legal_moves())
        board.apply_move(ply1)
        ply2 = choice(board.get_legal_moves())
        starting_position_list.append((ply1, ply2))

    print(DESCRIPTION)
    for agentUT in test_agents:
        print("")
        print("*************************")
        print("{:^25}".format("Evaluating: " + agentUT.name))
        print("*************************")

        agents = random_agents + mm_agents + ab_agents + [agentUT]
        win_ratio = play_tournament(agents, starting_position_list)

        print("\n\nResults:")
        print("----------")
        print("{!s:<15}{:>10.2f}%".format(agentUT.name, win_ratio))


if __name__ == "__main__":
    main()
