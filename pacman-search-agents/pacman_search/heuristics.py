from __future__ import annotations

from collections.abc import Iterable

from .maze import Position, State


def manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def spanning_tree_bound(current: Position, remaining: Iterable[Position]) -> float:
    """Lower bound: connect current to a nearest goal and span all other goals."""
    goals = set(remaining)
    if not goals:
        return 0.0
    bound = min(manhattan(current, goal) for goal in goals)
    tree = {goals.pop()}
    while goals:
        distance, goal = min(
            (manhattan(a, b), b)
            for a in tree
            for b in goals
        )
        bound += distance
        tree.add(goal)
        goals.remove(goal)
    return float(bound)


def goal_heuristic(state: State, name: str) -> float:
    position, remaining = state
    if name == "zero":
        return 0.0
    if name == "nearest":
        return float(min((manhattan(position, goal) for goal in remaining), default=0))
    if name == "mst":
        return spanning_tree_bound(position, remaining)
    raise ValueError(f"unknown heuristic: {name}")

