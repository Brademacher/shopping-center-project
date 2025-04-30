"""Multi-Goal A* agent (greedy version)

This agent repeatedly plans an A* path to the *nearest* unvisited goal,
executes that path one step at a time, and replans whenever it reaches a
store.  The episode ends **only when**
    • at least ``min_stores`` distinct stores have been visited **and**
    • the compulsory ``must_visit`` store (if supplied) has also been visited.

It pairs with ``algorithms/mgastar.py`` (a greedy multi‑goal planner).
The strategy is *not* optimal for the full travelling‑salesman–like problem
but is fast and memory‑light for large grids.
"""
from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

# --- project imports ---------------------------------------------------
# If your folder layout differs, adjust the import below accordingly.
from algorithms.mgastar import MultiGoalAStarPlanner

# Position = (x, y, floor)
Pos = Tuple[int, int, int]


class MultiGoalAStarAgent:
    """Agent that uses a *greedy* Multi‑Goal A* planner.

    Parameters
    ----------
    env : MallEnvironment
        Simulation environment exposing:
          • ``agent_pos``  – current position (Pos)
          • ``stores``     – set/list of store coordinates (Pos)
          • ``visited_stores`` – mutable set recording visited stores
          • ``goal_reached`` – boolean flag the agent may set
          • ``move_agent(next_pos)`` – execute a move
    planner : MultiGoalAStarPlanner
        Planner that can
          • ``choose_next_goal(current, visited) -> Pos | None``
          • ``astar(start, goal) -> List[Pos]`` (inclusive of start & goal)
    must_visit : Optional[Pos]
        A compulsory store that *must* be visited before termination.
    min_stores : int, default 6
        Minimum number of distinct stores to visit.
    max_steps : int, default 100_000
        Failsafe upper bound on total moves.
    """

    def __init__(
        self,
        env,
        planner: MultiGoalAStarPlanner,
        *,
        must_visit: Optional[Pos] = None,
        min_stores: int = 6,
        max_steps: int = 100_000,
    ) -> None:
        self.env = env
        self.planner = planner
        self.must_visit = must_visit
        self.min_stores = min_stores
        self.max_steps = max_steps

        # Internal state -------------------------------------------------
        self._step_counter = 0
        self._current_path: List[Pos] = []  # remaining moves

    # ------------------------------------------------------------------
    # Main loop helper expected by evaluate_simulations.py
    # ------------------------------------------------------------------
    def step(self) -> bool:
        """Perform **one** time‑step.

        Returns ``True`` while the episode should continue, ``False`` when
        the termination criteria have been met.
        """
        # --- guard against runaway loops --------------------------------
        if self._step_counter >= self.max_steps:
            self.env.goal_reached = True
            return False

        # --- (re)plan if no path remains --------------------------------
        if not self._current_path:
            goal = self.planner.choose_next_goal(
                self.env.agent_pos, self.env.visited_stores
            )
            if goal is None:
                # No reachable unvisited goals remain – stop.
                self.env.goal_reached = True
                return False

            full_path, _ = self.planner.astar(self.env.agent_pos, goal, self.env)
            # Remove current cell so that the *next* pos is where we move.
            self._current_path = full_path[1:]

        # --- execute one move (if any) ----------------------------------
        if self._current_path:
            next_pos = self._current_path.pop(0)
            self.env.move_agent(next_pos)

        self._step_counter += 1

        # --- handle arriving at a store ---------------------------------
        if (
            self.env.agent_pos in self.env.stores
            and self.env.agent_pos not in self.env.visited_stores
        ):
            self.env.visited_stores.add(self.env.agent_pos)
            self._current_path.clear()  # force replan next tick

        # Check if goal condition is now met after visiting
        if (
            len(self.env.visited_stores) >= self.min_stores and
            (self.must_visit is None or self.must_visit in self.env.visited_stores)
        ):
            self.env.goal_reached = True
            return False

        # --- termination test -------------------------------------------
        enough = len(self.env.visited_stores) >= self.min_stores
        trigger_ok = (
            self.must_visit is None or self.must_visit in self.env.visited_stores
        )
        done = enough and trigger_ok
        self.env.goal_reached = done
        return not done

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    @staticmethod
    def compute_path_cost(path: Sequence[Pos]) -> int:
        """Grid with unit costs ⇒ cost == number of moves."""
        return max(0, len(path) - 1)