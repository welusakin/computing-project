import unittest

from pacman_search.heuristics import goal_heuristic
from pacman_search.maze import Maze
from pacman_search.search import search


LAYOUT = """\
#########
#P  #  .#
# #    .#
#   #   #
#########
"""


class SearchAgentTests(unittest.TestCase):
    def setUp(self):
        self.maze = Maze.from_text(LAYOUT)
        self.start = (self.maze.start, self.maze.food)

    def run_algorithm(self, algorithm, heuristic=None):
        return search(
            self.start,
            lambda state: list(self.maze.successors(state)),
            lambda state: not state[1],
            algorithm,
            heuristic,
        )

    def test_bfs_ucs_and_astar_find_same_shortest_food_path(self):
        bfs = self.run_algorithm("bfs")
        ucs = self.run_algorithm("ucs")
        astar = self.run_algorithm(
            "astar", lambda state: goal_heuristic(state, "mst")
        )
        self.assertIsNotNone(bfs)
        self.assertEqual(bfs.cost, ucs.cost)
        self.assertEqual(bfs.cost, astar.cost)
        self.assertEqual(len(astar.actions), astar.cost)

    def test_path_collects_every_food_cell(self):
        result = self.run_algorithm(
            "astar", lambda state: goal_heuristic(state, "nearest")
        )
        self.assertIsNotNone(result)
        position = self.maze.start
        remaining = set(self.maze.food)
        deltas = {"North": (0, -1), "South": (0, 1), "West": (-1, 0), "East": (1, 0)}
        for action in result.actions:
            dx, dy = deltas[action]
            position = (position[0] + dx, position[1] + dy)
            remaining.discard(position)
        self.assertFalse(remaining)

    def test_unreachable_food_returns_no_solution(self):
        maze = Maze.from_text("#####\n#P#.#\n#####\n")
        start = (maze.start, maze.food)
        result = search(
            start,
            lambda state: list(maze.successors(state)),
            lambda state: not state[1],
            "astar",
            lambda state: goal_heuristic(state, "mst"),
        )
        self.assertIsNone(result)

    def test_corner_astar_matches_bfs(self):
        corners = self.maze.corners()
        start = (self.maze.start, frozenset(corners - {self.maze.start}))
        successors = lambda state: list(self.maze.successors(state))
        goal = lambda state: not state[1]
        bfs = search(start, successors, goal, "bfs")
        astar = search(
            start,
            successors,
            goal,
            "astar",
            lambda state: goal_heuristic(state, "mst"),
        )
        self.assertIsNotNone(bfs)
        self.assertEqual(bfs.cost, astar.cost)

    def test_invalid_algorithm_is_rejected(self):
        with self.assertRaises(ValueError):
            self.run_algorithm("greedy")


if __name__ == "__main__":
    unittest.main()
