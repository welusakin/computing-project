from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

Position = tuple[int, int]
State = tuple[Position, frozenset[Position]]
MOVES: tuple[tuple[str, int, int], ...] = (
    ("North", 0, -1),
    ("South", 0, 1),
    ("West", -1, 0),
    ("East", 1, 0),
)


@dataclass(frozen=True)
class Maze:
    rows: tuple[str, ...]
    start: Position
    food: frozenset[Position]
    open_cells: frozenset[Position]

    @classmethod
    def from_file(cls, path: str | Path) -> "Maze":
        return cls.from_text(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_text(cls, text: str) -> "Maze":
        rows = tuple(line.rstrip("\n\r") for line in text.splitlines() if line.strip())
        if not rows:
            raise ValueError("maze is empty")
        width = max(map(len, rows))
        rows = tuple(row.ljust(width, "#") for row in rows)
        starts: list[Position] = []
        food: set[Position] = set()
        open_cells: set[Position] = set()
        for y, row in enumerate(rows):
            for x, tile in enumerate(row):
                if tile != "#":
                    open_cells.add((x, y))
                if tile == "P":
                    starts.append((x, y))
                elif tile == ".":
                    food.add((x, y))
        if len(starts) != 1:
            raise ValueError(f"maze must contain exactly one P start; found {len(starts)}")
        if not food:
            raise ValueError("maze must contain at least one . food cell")
        return cls(rows, starts[0], frozenset(food), frozenset(open_cells))

    def successors(self, state: State) -> Iterable[tuple[str, State, float]]:
        (x, y), remaining = state
        for action, dx, dy in MOVES:
            next_position = (x + dx, y + dy)
            if next_position not in self.open_cells:
                continue
            next_remaining = remaining - {next_position}
            yield action, (next_position, frozenset(next_remaining)), 1.0

    def corners(self) -> frozenset[Position]:
        """Return the four extreme open cells of the grid."""
        min_x = min(x for x, _ in self.open_cells)
        max_x = max(x for x, _ in self.open_cells)
        min_y = min(y for _, y in self.open_cells)
        max_y = max(y for _, y in self.open_cells)
        result = {
            point
            for point in ((min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y))
            if point in self.open_cells
        }
        if len(result) < 2:
            raise ValueError("maze needs at least two open corners for the corners objective")
        return frozenset(result)

    def render_path(self, path: list[str]) -> str:
        grid = [list(row) for row in self.rows]
        position = self.start
        deltas = {name: (dx, dy) for name, dx, dy in MOVES}
        for action in path:
            dx, dy = deltas[action]
            position = (position[0] + dx, position[1] + dy)
            x, y = position
            if grid[y][x] == ".":
                grid[y][x] = "*"
            elif grid[y][x] == " ":
                grid[y][x] = "+"
        x, y = self.start
        grid[y][x] = "P"
        return "\n".join("".join(row).rstrip() for row in grid)

