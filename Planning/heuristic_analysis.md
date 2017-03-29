# Planning search - Heuristic analysis

In this project, I implemented a planning search agent to solve deterministic logistics planning problems for an Air Cargo transport system. 

This agent can either use uninformed search algorithms or heuristic search algorithms with domain-independent heuristics. 

This write up essentially benchmarks a range of search algorithms against 3 planning problems of increasing size.

## Problems

### Air Cargo action schema

All three problems have the same action schema, defined below in PDDL:

```
Action(Load(c, p, a),
	PRECOND: At(c, a) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
	EFFECT: ¬ At(c, a) ∧ In(c, p))
Action(Unload(c, p, a),
	PRECOND: In(c, p) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
	EFFECT: At(c, a) ∧ ¬ In(c, p))
Action(Fly(p, from, to),
	PRECOND: At(p, from) ∧ Plane(p) ∧ Airport(from) ∧ Airport(to)
	EFFECT: ¬ At(p, from) ∧ At(p, to))
```

They differ by their initial states and goals

### Problem 1

```
Init(At(C1, SFO) ∧ At(C2, JFK) 
	∧ At(P1, SFO) ∧ At(P2, JFK) 
	∧ Cargo(C1) ∧ Cargo(C2) 
	∧ Plane(P1) ∧ Plane(P2)
	∧ Airport(JFK) ∧ Airport(SFO))
Goal(At(C1, JFK) ∧ At(C2, SFO))
```

An optimal plan for this problem is the following:

```
Load(C1, P1, SFO)
Fly(P1, SFO, JFK)
Unload(C1, P1, JFK)
Load(C2, P2, JFK)
Fly(P2, JFK, SFO)
Unload(C2, P2, SFO)
```

### Problem 2

```
Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) 
	∧ At(P1, SFO) ∧ At(P2, JFK) ∧ At(P3, ATL) 
	∧ Cargo(C1) ∧ Cargo(C2) ∧ Cargo(C3)
	∧ Plane(P1) ∧ Plane(P2) ∧ Plane(P3)
	∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL))
Goal(At(C1, JFK) ∧ At(C2, SFO) ∧ At(C3, SFO))
```

An optimal plan for this problem is the following:

```
Load(C1, P1, SFO)
Fly(P1, SFO, JFK)
Unload(C1, P1, JFK)
Load(C2, P2, JFK)
Fly(P2, JFK, SFO)
Unload(C2, P2, SFO)
Load(C3, P3, ATL)
Fly(P3, ATL, SFO)
Unload(C3, P3, SFO)
```

### Problem 3

```
Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) ∧ At(C4, ORD) 
	∧ At(P1, SFO) ∧ At(P2, JFK) 
	∧ Cargo(C1) ∧ Cargo(C2) ∧ Cargo(C3) ∧ Cargo(C4)
	∧ Plane(P1) ∧ Plane(P2)
	∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL) ∧ Airport(ORD))
Goal(At(C1, JFK) ∧ At(C3, JFK) ∧ At(C2, SFO) ∧ At(C4, SFO))
```

An optimal plan for this problem is the following:

```
Load(C1, P1, SFO)
Fly(P1, SFO, ATL)
Load(C3, P1, ATL)
Fly(P1, ATL, JFK)
Unload(C3, P1, JFK)
Unload(C1, P1, JFK)
Load(C2, P2, JFK)
Fly(P2, JFK, ORD)
Load(C4, P2, ORD)
Fly(P2, ORD, SFO)
Unload(C4, P2, SFO)
Unload(C2, P2, SFO)
```

## Uninformed search

The following tables provide metrics on number of node expansions required, number of goal tests, number of new nodes, length of solution and time elapsed on each problem for the following 5 uninformed search algorithms:
- Breadth First Graph Search
- Breadth First Tree Search
- Depth First Graph Search
- Depth Limited Search (max depth = 50)
- Uniform Cost Search

*Problem 1*
					
| Algorithm |Expansions | Goal Tests | New Nodes | Plan length | Time elapsed (s) |
|:---------:|:---------:|:----------:|:---------:|:-----------:|:----------------:|
| DFGS      | 21        | 22         | 84        | 20          | 0.027            |
| DLS       | 101       | 271        | 414       | 50          | 0.150            |
| BFTS      | 1458      | 1459       | 5960      | 6           | 1.689            |
| BFGS      | 43        | 56         | 180       | 6           | 0.068            |
| UCS       | 55        | 57         | 224       | 6           | 0.069            |

*Problem 2*
					
| Algorithm |Expansions | Goal Tests | New Nodes | Plan length | Time elapsed (s) |
|:---------:|:---------:|:----------:|:---------:|:-----------:|:----------------:|
| DFGS      | 107       | 108        | 959       | 105         | 0.573            |
| DLS       | N/A       | N/A        | N/A       | N/A         | > 600            |
| BFTS      | N/A       | N/A        | N/A       | N/A         | > 600            |
| BFGS      | 3346      | 4612       | 30534     | 9           | 21.014           |
| UCS       | 4853      | 4855       | 44041     | 9           | 56.011           |

*Problem 3*
					
| Algorithm |Expansions | Goal Tests | New Nodes | Plan length | Time elapsed (s) |
|:---------:|:---------:|:----------:|:---------:|:-----------:|:----------------:|
| DFGS      | 292       | 293        | 2399      | 288         | 2.299            |
| DLS       | N/A       | N/A        | N/A       | N/A         | > 600            |
| BFTS      | N/A       | N/A        | N/A       | N/A         | > 600            |
| BFGS      | 14120     | 17673      | 124926    | 12          | 141.464          |
| UCS       | 18222     | 18224      | 159608    | 12          | 496.580          |

These numbers illustrate the main differences between these algorithms:
- If the solution state space is dense, Depth First Search can find a solution really quickly by expanding very few nodes, but it is not optimal (nor even good).
- Depth Limited Search has roughly the same pros and cons. By limiting the plan length, it avoids the worse solutions. But if this limit is set too high it can still yield rather bad plans (50 actions against 6 for an optimal plan on problem 1), and if it is set too low, it can become extremely slow (problems 2 and 3).
- Breadth First Search is optimal but slower. The graph search variant decreases significantly the number of node expansions compared to the tree search variant by avoiding previously explored nodes. This allows handling bigger toy problems like problems 2 and 3.
- Here, Uniform Cost Search is pretty much equivalent to Breadth First Search, as the cost of each action is 1.

## Heuristic search

The following tables provide the same metrics on each problem using the A* algorithm and each of the 3 following heuristics:
- `h_1` returns the same uninformative value of 1 for all nodes
- `h_pg_levelsum` uses a planning graph representation of the problemstate space to estimate the sum of all actions that must be carried out from the current state in order to satisfy each individual goal condition.
- `h_ignore_preconditions` estimates the minimum number of actions that must be carried out in order to satisfy all of the goal conditions by ignoring the preconditions required for an action to be executed.
					
| Heuristic                   |Expansions | Goal Tests | New Nodes | Plan length | Time elapsed (s) |
|:---------------------------:|:---------:|:----------:|:---------:|:-----------:|:----------------:|
| `h_1`                       | 55        | 57         | 224       | 6           | 0.069            |
| `h_pg_levelsum`             | 11        | 13         | 50        | 6           | 2.457            |
| `h_ignore_preconditions`    | 41        | 43         | 170       | 6           | 0.054            |

*Problem 2*
					
| Heuristic                |Expansions | Goal Tests | New Nodes | Plan length | Time elapsed (s) |
|:------------------------:|:---------:|:----------:|:---------:|:-----------:|:----------------:|
| `h_1`                    | 4853      | 4855       | 44041     | 9           | 57.012           |
| `h_pg_levelsum`          | 86        | 88         | 841       | 9           | 305.586          |
| `h_ignore_preconditions` | 1506      | 1508       | 13820     | 9           | 18.812           |

*Problem 3*
					
| Heuristic                |Expansions | Goal Tests | New Nodes | Plan length | Time elapsed (s) |
|:------------------------:|:---------:|:----------:|:---------:|:-----------:|:----------------:|
| `h_1`                    | 18222     | 18224      | 159608    | 12          | 469.878          |
| `h_pg_levelsum`          | N/A       | N/A        | N/A       | N/A         | > 600            |
| `h_ignore_preconditions` | 5118      | 5120       | 45650     | 12          | 117.349          |

- Because the `h_1` heuristic is completely uninformative, using it with A* is equivalent to using Uniform Cost Search. It is optimal, but not an improvement over uninformed search.
- `h_pg_levelsum` is a consistent and rather precise heuristic. `A*` with `h_pg_levelsum` is thus optimal, and expands a lot fewer nodes than uninformed search algorithms. However, building a planning graph is so expensive that `A*` with `h_pg_levelsum` is slower than Breadth First Search!
- `h_ignore_preconditions` is another consistent heuristic, with a better balance between computational cost and precision. `A*` with `h_ingore_precdonitions` is optimal and slightly better than non-heuristic search planning methods for all three problems. It is the best heuristic developed in this project.

