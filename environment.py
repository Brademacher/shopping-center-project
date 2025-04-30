"""MallEnvironment – corrected
================================
This file now *parses and runs* (all indents/braces/parentheses closed) and
implements every interface expected by your agents and evaluation script.
"""
from __future__ import annotations

import json
import random
from typing import Dict, List, Set, Tuple

Pos = Tuple[int, int, int]


class MallEnvironment:
    """3‑D shopping‑centre grid world."""

    # ------------------------------------------------------------------
    # Construction ------------------------------------------------------
    # ------------------------------------------------------------------
    def __init__(
        self,
        length: int,
        width: int,
        floor: int,
        *,
        num_stores: int = 0,
        num_obstacles: int = 0,
        num_elevators: int = 0,
        num_escalators: int = 0,
    ) -> None:
        self.length = length
        self.width = width
        self.floor = floor
        self.start: Pos = (0, 0, 0)

        self.num_stores = num_stores
        self.num_obstacles = num_obstacles
        self.num_elevators = num_elevators
        self.num_escalators = num_escalators

        # Runtime state -------------------------------------------------
        self.agent_position: Pos = self.start
        self.goal_store_trigger_index: int | None = None
        self.goal_reached: bool = False

        # World representation -----------------------------------------
        self.grid = self._create_empty_grid()
        self.obstacles: Dict[Pos, bool] = {}
        self.elevators: Dict[str, Dict] = {}
        self.escalators: Dict[str, Dict] = {}
        self.stores: List[Pos] = []
        self.visited_stores: Set[Pos] = set()

        self.grid[self.start[2]][self.start[1]][self.start[0]] = 0  # reserve start

        self._place_obstacles()
        self._place_elevators()
        self._place_escalators()
        self._place_stores()

    # ------------------------------------------------------------------
    # Compatibility alias ----------------------------------------------
    # ------------------------------------------------------------------
    @property
    def agent_pos(self) -> Pos:
        return self.agent_position

    # ------------------------------------------------------------------
    # Movement ----------------------------------------------------------
    # ------------------------------------------------------------------
    def move_agent(self, next_pos: Pos) -> bool:
        x, y, f = next_pos
        if not (0 <= x < self.length and 0 <= y < self.width and 0 <= f < self.floor):
            return False
        if self.grid[f][y][x] == "X":
            return False
        self.agent_position = next_pos
        self.visit_store(x, y, f)
        return True

    # ------------------------------------------------------------------
    # World generation helpers -----------------------------------------
    # ------------------------------------------------------------------
    def _create_empty_grid(self):
        return [[[0 for _ in range(self.length)] for _ in range(self.width)] for _ in range(self.floor)]

    def _place_obstacles(self):
        placed = 0
        while placed < self.num_obstacles:
            f = random.randint(0, self.floor - 1)
            x = random.randint(1, self.length - 2)
            y = random.randint(1, self.width - 2)
            if (x, y, f) != self.start and self.grid[f][y][x] == 0:
                self.grid[f][y][x] = "X"
                self.obstacles[(x, y, f)] = True
                placed += 1

    def _place_elevators(self):
        placed = 0
        while placed < self.num_elevators:
            x = random.randint(0, self.length - 1)
            y = random.randint(0, self.width - 1)
            if (x, y) != self.start[:2] and all(self.grid[f][y][x] == 0 for f in range(self.floor)):
                label = f"E{placed + 1}"
                for f in range(self.floor):
                    self.grid[f][y][x] = label
                self.elevators[label] = {"coords": (x, y), "floors": list(range(self.floor))}
                placed += 1

    def _place_escalators(self):
        placed = 0
        while placed < self.num_escalators:
            f = random.randint(0, self.floor - 2)
            x = random.randint(0, self.length - 1)
            y = random.randint(1, self.width - 2)
            dy = random.choice([-1, 1])
            y_upper = y + dy
            if (
                (x, y, f) != self.start
                and self.grid[f][y][x] == 0
                and self.grid[f + 1][y_upper][x] == 0
            ):
                label = f"ES{placed + 1}"
                self.grid[f][y][x] = label + "↑"
                self.grid[f + 1][y_upper][x] = label + "↓"
                self.escalators[label] = {
                    "lower_coords": (x, y, f),
                    "upper_coords": (x, y_upper, f + 1),
                    "from_to": (f, f + 1),
                }
                placed += 1

    def _place_stores(self):
        placed = 0
        while placed < self.num_stores:
            f = random.randint(0, self.floor - 1)
            side = random.choice(["top", "bottom", "left", "right"])
            if side in ("top", "bottom"):
                y = 0 if side == "top" else self.width - 1
                x = random.randint(0, self.length - 1)
            else:
                x = 0 if side == "left" else self.length - 1
                y = random.randint(0, self.width - 1)
            if (
                self.grid[f][y][x] == 0
                and (x, y, f) != self.start
                and (x, y, f) not in self.obstacles
                and all((x, y) != elev["coords"] for elev in self.elevators.values())
                and all(
                    (x, y, f) not in (esc["lower_coords"], esc["upper_coords"]) for esc in self.escalators.values()
                )
            ):
                self.grid[f][y][x] = "S"
                self.stores.append((x, y, f))
                placed += 1

    # ------------------------------------------------------------------
    # Store/goal logic --------------------------------------------------
    # ------------------------------------------------------------------
    def set_goal_trigger_index(self, index: int):
        if not 0 <= index < self.num_stores:
            raise ValueError("Invalid store goal index")
        self.goal_store_trigger_index = index

    def visit_store(self, x: int, y: int, f: int):
        pos = (x, y, f)
        if pos in self.stores:
            self.visited_stores.add(pos)
        if (
            self.goal_store_trigger_index is not None
            and len(self.visited_stores) > self.goal_store_trigger_index
        ):
            self.goal_reached = True

    # ------------------------------------------------------------------
    # Neighbour helper --------------------------------------------------
    # ------------------------------------------------------------------
    def get_neighbors(self, x: int, y: int, f: int):
        nbrs: List[Tuple[int, int, int, float]] = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.length and 0 <= ny < self.width and self.grid[f][ny][nx] != "X":
                nbrs.append((nx, ny, f, 1))
        for elev in self.elevators.values():
            ex, ey = elev["coords"]
            if (x, y) == (ex, ey):
                for fl in elev["floors"]:
                    if fl != f and self.grid[fl][y][x] != "X":
                        nbrs.append((x, y, fl, 1.5 * abs(fl - f)))
        for esc in self.escalators.values():
            if (x, y, f) == esc["lower_coords"]:
                ux, uy, uf = esc["upper_coords"]
                if self.grid[uf][uy][ux] != "X":
                    nbrs.append((ux, uy, uf, 2))
        return nbrs

    # ------------------------------------------------------------------
    # JSON I/O ----------------------------------------------------------
    # ------------------------------------------------------------------
    def to_json(self, path: str):
        data = {
            "length": self.length,
            "width": self.width,
            "floor": self.floor,
            "grid": self.grid,
            "stores": [list(pos) for pos in self.stores],
            "obstacles": [list(pos) for pos in self.obstacles],
            "elevators": self.elevators,
            "escalators": self.escalators,
            "goal_store_trigger_index": self.goal_store_trigger_index
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> MallEnvironment:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        env = cls(
            length=data["length"],
            width=data["width"],
            floor=data["floor"],
            num_stores=0,
            num_obstacles=0,
            num_elevators=0,
            num_escalators=0,
        )

        env.grid = data["grid"]
        env.stores = [tuple(s) for s in data["stores"]]
        env.obstacles = {tuple(pos): True for pos in data["obstacles"]}
        env.elevators = data["elevators"]
        env.escalators = data["escalators"]
        env.goal_store_trigger_index = data.get("goal_store_trigger_index", None)

        env.agent_position = env.start
        env.visited_stores = set()
        env.goal_reached = False

        return env
