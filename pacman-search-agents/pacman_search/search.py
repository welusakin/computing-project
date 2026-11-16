from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from time import perf_counter
from typing import Callable

from .maze import State

Successors = Callable[[State], list[tuple[str, State, float]]]
GoalTest = Callable[[State], bool]
Heuristic = Callable[[State], float]


@dataclass
class SearchResult:
    algorithm: str
    actions: list[str]
    cost: float
    expanded: int
    generated: int
    elapsed_ms: float


def search(
    start: State,
    successors: Successors,
    is_goal: GoalTest,
    algorithm: str,
    heuristic: Heuristic | None = None,
) -> SearchResult | None:
    """Run DFS, BFS, UCS, or A* with graph-search duplicate handling."""
    algorithm = algorithm.lower()
    if algorithm not in {"dfs", "bfs", "ucs", "astar"}:
        raise ValueError("algorithm must be dfs, bfs, ucs, or astar")
    h = heuristic or (lambda _state: 0.0)
    started = perf_counter()
    generated = 1
    expanded = 0

    if algorithm in {"dfs", "bfs"}:
        frontier = [(start, [], 0.0)] if algorithm == "dfs" else deque([(start, [], 0.0)])
        seen: set[State] = set()
        while frontier:
            state, actions, cost = frontier.pop() if algorithm == "dfs" else frontier.popleft()
            if state in seen:
                continue
            seen.add(state)
            if is_goal(state):
                return SearchResult(algorithm, actions, cost, expanded, generated,
                                    (perf_counter() - started) * 1000)
            expanded += 1
            children = list(successors(state))
            if algorithm == "dfs":
                children.reverse()
            for action, child, step_cost in children:
                if child not in seen:
                    frontier.append((child, actions + [action], cost + step_cost))
                    generated += 1
        return None

    serial = count()
    frontier: list[tuple[float, int, float, State, list[str]]] = []
    heappush(frontier, (h(start) if algorithm == "astar" else 0.0,
                        next(serial), 0.0, start, []))
    best_cost: dict[State, float] = {start: 0.0}
    while frontier:
        _priority, _order, cost, state, actions = heappop(frontier)
        if cost != best_cost.get(state):
            continue
        if is_goal(state):
            return SearchResult(algorithm, actions, cost, expanded, generated,
                                (perf_counter() - started) * 1000)
        expanded += 1
        for action, child, step_cost in successors(state):
            new_cost = cost + step_cost
            if new_cost >= best_cost.get(child, float("inf")):
                continue
            best_cost[child] = new_cost
            priority = new_cost + (h(child) if algorithm == "astar" else 0.0)
            heappush(frontier, (priority, next(serial), new_cost, child,
                                actions + [action]))
            generated += 1
    return None

