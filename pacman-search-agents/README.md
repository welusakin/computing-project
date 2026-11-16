# Pac-Man Search Agents

A complete, self-contained search-agent project for Pac-Man-style mazes. It models the agent's position and remaining goals, computes routes through configurable maps, and compares classic uninformed and informed search strategies. The implementation uses only the Python standard library.

## Problem model

- `#` cells are walls; spaces are walkable floor; `P` marks Pac-Man; `.` marks food.
- A state contains Pac-Man's grid position and the set of remaining goals.
- A move travels one open cell in one of four cardinal directions.
- A food-search goal is reached after collecting every food cell.
- A corner-search goal is reached after visiting every detected maze corner.

## Algorithms

- **Depth-first search (DFS):** explores a branch deeply before backtracking; useful for seeing how expansion order affects a non-optimal search.
- **Breadth-first search (BFS):** explores by depth and returns a shortest path when each move has equal cost.
- **Uniform-cost search (UCS):** expands the frontier with the lowest accumulated path cost; in this unit-cost grid it provides the cost-based baseline.
- **A* search:** combines accumulated path cost with a lower-bound estimate of the remaining travel.
- **Corner heuristic:** uses the nearest remaining corner plus a minimum spanning tree over the remaining corners.
- **Food heuristic:** uses the nearest remaining food plus a minimum spanning tree over remaining food locations.

The heuristic is admissible for the project's four-direction, unit-step movement model. Metrics report path cost, path length, generated states, expanded states, and elapsed time so algorithm behavior can be compared directly.

## Run

From this directory, run A* on the included multi-corridor map and print the route:

```bash
python3 -m pacman_search --algorithm astar --goal food --show-path
```

Compare algorithms on the food objective:

```bash
python3 -m pacman_search --compare --goal food
```

Use the corners objective:

```bash
python3 -m pacman_search --algorithm astar --goal corners --show-path
```

Add or edit ASCII layouts in `maps/` and pass one with `--map maps/your-map.txt`. Run the correctness checks with `python3 -m unittest discover -s tests -v`.

Available algorithms are `dfs`, `bfs`, `ucs`, and `astar`; goals are `food` and `corners`. Use `--help` for the complete command syntax.

## Code map

- `pacman_search/maze.py` parses the ASCII grid and defines legal moves and goals.
- `pacman_search/search.py` implements the four frontier strategies and records metrics.
- `pacman_search/heuristics.py` contains Manhattan-distance and spanning-tree lower bounds.
- `pacman_search/cli.py` provides the command-line runner and comparison report.
- `maps/medium.txt` is a multi-corridor map with walls and food goals.
- `tests/test_search.py` checks shortest-path agreement, goal collection, unreachable goals, and invalid algorithms.

This is an independently rebuilt version based on the project details available here. The original course starter framework and submission files were not available.
