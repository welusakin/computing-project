from __future__ import annotations

import argparse
from pathlib import Path

from .heuristics import goal_heuristic
from .maze import Maze, State
from .search import SearchResult, search


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare classic search agents on a Pac-Man grid.")
    parser.add_argument("--algorithm", choices=("dfs", "bfs", "ucs", "astar"), default="astar")
    parser.add_argument("--goal", choices=("food", "corners"), default="food")
    parser.add_argument("--heuristic", choices=("nearest", "mst"), default="mst")
    parser.add_argument("--map", type=Path, default=Path(__file__).parent.parent / "maps" / "medium.txt")
    parser.add_argument("--compare", action="store_true", help="run all four algorithms and compare metrics")
    parser.add_argument("--show-path", action="store_true", help="print the sequence of moves")
    return parser


def run_one(maze: Maze, goal: str, algorithm: str, heuristic: str) -> SearchResult | None:
    targets = maze.food if goal == "food" else maze.corners()
    start: State = (maze.start, frozenset(targets - {maze.start}))
    result = search(
        start,
        lambda state: list(maze.successors(state)),
        lambda state: not state[1],
        algorithm,
        lambda state: goal_heuristic(state, "zero" if algorithm != "astar" else heuristic),
    )
    return result


def print_result(result: SearchResult | None, maze: Maze, show_path: bool) -> None:
    if result is None:
        print("No solution found.")
        return
    print(f"Algorithm: {result.algorithm.upper()}")
    print(f"Path cost: {result.cost:g}")
    print(f"Moves: {len(result.actions)}")
    print(f"Expanded states: {result.expanded}")
    print(f"Generated states: {result.generated}")
    print(f"Elapsed: {result.elapsed_ms:.3f} ms")
    if show_path:
        print("Actions: " + " -> ".join(result.actions))
        print("\n" + maze.render_path(result.actions))


def main() -> int:
    args = build_parser().parse_args()
    try:
        maze = Maze.from_file(args.map)
        if args.compare:
            print(f"Objective: collect all {args.goal} goals\n")
            print(f"{'Algorithm':<11} {'Cost':>7} {'Expanded':>10} {'Generated':>11} {'Time ms':>10}")
            for algorithm in ("dfs", "bfs", "ucs", "astar"):
                result = run_one(maze, args.goal, algorithm, args.heuristic)
                if result is None:
                    print(f"{algorithm.upper():<11} no solution")
                else:
                    print(f"{result.algorithm.upper():<11} {result.cost:>7.0f} {result.expanded:>10} "
                          f"{result.generated:>11} {result.elapsed_ms:>10.3f}")
            return 0
        print_result(run_one(maze, args.goal, args.algorithm, args.heuristic), maze, args.show_path)
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 2

