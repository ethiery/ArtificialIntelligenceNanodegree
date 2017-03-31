# Research review - Historical Developments in AI Planning and Search

A first historical development in the field was the development of *STRIPS* (Fikes and Nilsson, 1971), the first major planning system, at the Stanford Research Institute. *STRIPS* was the planning component of Shakey the robot, the first general-purpose reasoning mobile robot, designed to navigate and push objects in a multi-room environment. The most influential part of this system was actually not the algorithms used, but its representation	language which was close to the "classical" language described in Udacity's AI nanodegree. The *STRIPS* language can be considered as the ancestor of the Action Description Language and the Problem Domain Description Language.

A second major development was the invention of the *GRAPHPLAN* system (Blum and Furst, 1995, 1997). It introduced a data structure called a *planning graph*, which can be used to search a sequence of actions solving a planning problem expressed in *STRIPS*, but also to derive heuristics as demonstrated in the project this research review is part of. A *planning graph* is basically an encoding of a planning problem that explicits useful constraints over the possible solutions, reducing rather drastically the amount of search required. It had a significant impact on the field of planning, being orders of magnitude faster than the partial-order planners that had dominated the field for the previous 20 years.

A third major development was *RePOP* (Nguyen and Kambhampati, 2001) which stands for Reviving Partial Order Planning. This paper challenged the assumption that partial order planning algorithms scale badly, by using heuristic control techniques to make them competitive with the currently successful planners. In addition to outperforming *GRAPHPLAN* on certain domains, *RePOP* generates plans that are more flexible. 

It is important to note that to date there is no clear "winner" in the planning field, as the performances of the different contenders depend on the class of problem to solve.


### Bibliography

[1] Stuart Russell, Peter Norvig; Artificial Intelligence: A Modern Ap-
proach (2nd ed.); Prentice Hall; 2003.

[2] https://en.wikipedia.org/wiki/STRIPS

[3] https://en.wikipedia.org/wiki/Shakey_the_robot

[4] https://en.wikipedia.org/wiki/Graphplan

[5] Nguyen, Kambhampati; Reviving Partial Order Planning; International Joint Conference on Artificial Intelligence 459-464; 2001
