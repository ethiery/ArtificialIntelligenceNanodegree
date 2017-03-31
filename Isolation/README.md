# Isolation

Isolation is a deterministic, two-player game of perfect information in which the players alternate turns moving a single piece from one cell to another on a board. Whenever either player occupies a cell, that cell becomes blocked for the remainder of the game.  The first player with no remaining legal moves loses, and the opponent is declared the winner.

This project uses a version of Isolation where each agent is restricted to L-shaped movements (like a knight in chess) on a rectangular grid (like a chess or checkerboard).  The agents can move to any open cell on the board that is 2-rows and 1-column or 2-columns and 1-row away from their current position on the board. Movements are blocked at the edges of the board (the board does not wrap around), however, the player can "jump" blocked or occupied spaces (just like a knight in chess).

Additionally, agents have a fixed time limit each turn to search for the best move and respond.  If the time limit expires during a player's turn, that player forfeits the match, and the opponent wins.

These rules are implemented in the `isolation.Board` and `isolation.Player` classes provided in the repository. The `Board` class is based on code provided as part of Udacity's Artificial Intelligence Nanodegree, but was optimised to be significantly faster (especially by reducing the time spent copying data).

# My game playing agent

My game playing agent is implemented in `game_agent.py` and is compatible with different heuristics implemented in `heuristics.py` and explained further below.


I started by implementing a fixed-depth minimax search in `CustomPlayer.minimax()` (see [AIMA Minimax Decision](https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md)). Then I added alpha-beta pruning in `CustomPlayer.alphabeta()` (see [AIMA Alpha-Beta Search](https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md)). Finally I implemented iterative deepening in `CustomPlayer.get_move()` (see [AIMA Iterative Deepening Search](https://github.com/aimacode/aima-pseudocode/blob/master/md/Iterative-Deepening-Search.md))

This was enough to pass the unit tests for the AI Nanodegree assignment, in `agent_test.py`.

I then went a bit further by :
- Trying to use a transposition table to avoid reevaluating certain moves. I was not able to get any performance improvement out of it, which makes sense as the probability of getting in the same state by taking two different paths is very low in this game.
- Reordering moves to maximize pruning opportunity in `CustomPlayer.alphabeta()`. That was very successful, consistently allowing to search several layers deeper in the game tree.

# Heuristics

`heuristics.py` contains 6 heuristics used to evaluate the utility of a game state for a player. The 3 first ones were sample heuristics given in the template code of the assignment, and the 3 others we designed and implemented by me.

## Sample heuristics

These 3 heuristics are used to form a set of various opponents to measure the relative performance of my agent (more details in the *Tournament* section).

### Null score

This very basic heuristic returns the utility value for terminal states, and the same uninformative value for all non terminal states. 

### Open move score

This simple heuristic evaluates a game state for a given player by the number of moves open for him on the board. It pushes the agent to keep his possibilities open, which is a good rule of thumb as the goal of the game is to be the last one moving. However, it does not take into consideration the opponent, which leads us to the next heuristic.

### Improved score

This heuristic returns the difference between the *open move score* for a given player, and the *open move score* for his opponent. This corrects the default of the previous heuristic, by pushing the agent to restrain his opponent's possibilities while keeping his possibilities open. It has the big advantage of being very fast to evaluate, allowing rather deep searches in the game tree.

## My heuristics

### Pure monte carlo score

A simple way to evaluate the utility of a game state for a player is to simulate a few random games from that state, and average the outcome. E.g. if from a given state 3 random roll-outs lead to a win, and 7 lead to a loss, the heuristic would return 3 * 1 + 7 * (-1) = -4. 

The number of roll-outs is a parameter, and a compromise has to be found between usefulness of the result and computing cost. I found that the heuristic performed better when the number was between 5 and 10.

A benefit of that heuristic is that it does not use any prior knowledge of the game. It can thus be used in general game play. An improved version of it can even completely replace the minimax search (see [Monte Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)). Also, it gives a good baseline: any heuristic that uses human knowledge in a smart way should outperform it.

### Reach score

Another default of the *open move score* is that it does not take into account what will happen after the next move. For example, a move can seem very unattractive because it leads to a game state where the player has only 1 open move, but this move can lead to a more open part of the board where the player should go to win. See [Horizon Effet](https://en.wikipedia.org/wiki/Horizon_effect)

To mitigate this issue, it would be better to have a heuristic that measure **the number of moves the player will be able to make before getting stuck assuming optimal opponent play**. 

A first upper bound for this number is the number of cells that are still available on the board. This estimation only depends on the number of the ply though, so it cannot help to make a decision. For example, when playing the 6-th ply of the game on a 7x7 board, all possible moves will lead to a board where 49 - 6 = 43 cells of the board are still available.

A more precise upper bound is the length of the longest path the player can follow in the cells that are still available. However, computing this value is NP-hard, so the computational cost is prohibitive even on a set of a few available cells (see [Longest Path Problem](https://en.wikipedia.org/wiki/Longest_path_problem)).

A compromise is the number of cells that are still reachable by the player. It can be computed by performing a simple breadth first search from the player's current position. To refine that estimation, we can also weight the reachable cells differently depending on how far they are. This encodes the knowledge that the greater the number of moves to reach a cell, the higher the probability that the opponent will prevent the player from reaching that cell.

More precisely, the `reach_score()` heuristic gives to each cell a weight equal to :
- `0` if the cell is not reachable
- `common_ratio ^ (1 - k)` if the cell is reachable in `k` moves, that is `1` for cells reachable in `1` move, `1 / common_ratio` for cells reachable in 2 moves, `1 / common_ratio²` for cells reachable in 3 moves etc.

`common_ratio` is a parameter that controls the decrease of the weight of a reachable cell with distance. 

I set up a small experiment to determine a good value for the ratio, at least against the 6 opponents described in the *Tournament* section (there is no guarantee that it would generalize well to other opponents). The key is to make sure that only the value of the ratio varies, and that all the rest stays the same. For that, I sampled a set of 100 random pairs of starting positions, then for different values of the ratio I made my agent play 200 games against each of the 6 opponents, with a 50 ms time limit, on a recent laptop. Playing 2 games per pair of starting positions with inverse roles for the agents allows to control for differences in outcome resulting from advantage due to starting position on the board.

| `common_ratio` | Win ratio |
|:--------------:|:---------:|
|  1.0           |  68.42 %  |
|  1.1           |  74.17 %  |
|  1.2           |  74.92 %  |
|  1.3           |  76.00 %  |
|  1.4           |  75.08 %  |
|  1.5           |  74.17 %  |

Considering the result above, I set the default value of `common_ratio` to `1.3`.

### Differential reach score

The *reach score* heuristic has the same bias as the *open move score* heuristic: it does not take the opponent into consideration. 

As with the *improve score* heuristic, this can be fixed by using the difference between the *reach score* of the player and the *reach score* of his opponent. That is what the *differential reach score* heuristic returns.

I ran the same experiment to see if the optimal `common_ratio` value for this heuristic is the same.

| `common_ratio` | Win ratio |
|:--------------:|:---------:|
|  1.0           |  68.67 %  |
|  1.1           |  76.42 %  |
|  1.2           |  77.42 %  |
|  1.3           |  77.75 %  |
|  1.4           |  78.50 %  |
|  1.5           |  77.08 %  |

It was not, so I set this default value to `1.4`.

## Tournament

### Setup

The `tournament.py` script is used to evaluate the relative performance of my 3 heuristics in a round-robin tournament against 6 other pre-defined agents: 
- `MM_Null`: agent using fixed-depth (depth 3) minimax search and the *null score* heuristic
- `MM_Open`: agent using fixed-depth (depth 3) minimax search and the *open move score* heuristic
- `MM_Improved`: agent using fixed-depth (depth 3) minimax search and the *improved score* heuristic
- `AB_Null`: agent using fixed-depth (depth 5) alpha-beta search and the *null score* heuristic
- `AB_Open`: agent using fixed-depth (depth 5) alpha-beta search and the *open move score* heuristic
- `AB_Improved`: agent using fixed-depth (depth 5) alpha-beta search and the *improved score* heuristic
- The initial AI nanodegree assignment also used an agent that randomly chooses a move each turn implemented in `sample_players.py`, but I found that it made comparisons less reliable, as this opponent performance varied a lot, even with the same initial positions.

The performance of time-limited iterative deepening search is hardware dependent (faster hardware is expected to search deeper than slower hardware in the same amount of time).  The script controls for these effects by also measuring the baseline performance of an agent using the *improved score* heuristic. 

Each of the 3 + 1 agents played 200 games against each of the 6 opponents (using a unique set of starting positions as explained earlier). The time limit was set to 50ms. The average depth reached by iterative deepening over all the games was also measured for each agent. 

###Results and analysis

The table below present the results of the tournament.

|                             | *Pure Monte Carlo* | *Reach* | *Differential reach* | *Improved* |
|:----------------------------|:------------------------:|:-------------:|:--------------------------:|:-----------------:|
| Win ratio vs `MM_Null`      | 151/200                  | 187/200       | 182/200                    | 183/200           |
| Win ratio vs `MM_Open`      | 107/200                  | 144/200       | 151/200                    | 142/200           |
| Win ratio vs `MM_Improved`  | 113/200                  | 133/200       | 139/200                    | 144/200           |
| Win ratio vs `AB_Null`      | 150/200                  | 179/200       | 174/200                    | 167/200           |
| Win ratio vs `AB_Open`      | 106/200                  | 135/200       | 138/200                    | 128/200           |
| Win ratio vs `AB_Improved`  | 108/200                  | 147/200       | 145/200                    | 143/200           |
| Average win ratio           | 61.25 %                  | 77.08 %       | 77.42 %                    | 75.58 %           |
| Average depth reached by ID | 7.41                     | 10.39         | 9.11                       | 12.66             |

Not surprisingly, the *Pure Monte Carlo* heuristic had the worst performance. This is partly due to :
- The fact that it does not benefit from any human knowledge. That explains the big difference on win ratio between another "dumb" heuristic like *Null score*, and smarter heuristics like *Open score* and *Improved score*.
- The cost of simulating roll outs (especially at the beginning of the game), which prevents from exploring many layers of the game tree (~7, only 2 more than the opponents using depth-limited alpha beta).


Both the *Reach score* and *Differential reach score* heuristics consistently outperformed the *Improved score* heuristic over the 1200 games they played, resulting in respectively 1.5 % and 2 % improvements of the win ratio. Even though the iterative deepening search is 2 or 3 plies shallower when using this 2 heuristics, they seem to be able to compensate by giving a better analysis of a board. 

Interestingly, the *Differential reach score* heuristic did only slightly better than the *Reach score* one. Even though it is twice as expensive to compute, I expected trying to trap the opponent to be more efficient than just focusing on your own pawn. It was not the case here, maybe because it can also favor riskier behaviours.

It is really hard to come up with plausible explanations because there are so many variables. Search depth seems to be one of them: while the *Open score* heuristic gave better results than the *Improved score* one when performing a search of depth 3 (`AB_*` opponents), it was the opposite when performing a search of depth 5 (`AB_*` opponents). It made me wonder if the *Reach score* heuristic could outperform the *Differential reach score* heuristic when allowed deeper searches, so I ran the tournament again but with a time limit of 200ms.

|                             | *Pure Monte Carlo* | *Reach* | *Differential reach* | *Improved* |
|:----------------------------|:------------------------:|:-------------:|:--------------------------:|:-----------------:|
| Win ratio vs `MM_Null`      | 174/200                  | 192/200       | 191/200                    | 193/200           |
| Win ratio vs `MM_Open`      | 138/200                  | 153/200       | 172/200                    | 160/200           |
| Win ratio vs `MM_Improved`  | 117/200                  | 135/200       | 162/200                    | 160/200           |
| Win ratio vs `AB_Null`      | 154/200                  | 187/200       | 186/200                    | 185/200           |
| Win ratio vs `AB_Open`      | 123/200                  | 145/200       | 146/200                    | 137/200           |
| Win ratio vs `AB_Improved`  | 136/200                  | 161/200       | 167/200                    | 165/200           |
| Average win ratio           | 70.17 %                  | 81.08 %       | 85.33 %                    | 83.33 %           |
| Average depth reached by ID | 10.85                    | 15.19         | 12.55                      | 17.04             |

In these conditions, *Differential reach score* was still the best heuristic, but *Reach score* no longer outperformed *Improve score*, which shows that sometimes searching deeper with a simpler heuristic is better. 

To finish, let see how these 3 heuristics perform against each other.
- *Reach score* vs *Differential reach score* : 179 - 221
- *Reach score* vs *Improved score* : 190 - 210
- *Improved score* vs *Differential reach score* : 203 - 197


In the end, I would thus advise using `Differential reach score`.

I think a good conclusion to this write up is that designing a heuristic should be an iterative process, because when so many variables are at play, only statistics over a big enough number of games can guide you reliably. 



