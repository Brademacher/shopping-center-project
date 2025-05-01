# agents/dstarlite_agent.py

from algorithms.dstarlite import DStarLitePlanner
from typing import List, Tuple

Coord = Tuple[int, int, int]

class DStarLiteAgent:
    def __init__(self):
        # no planner here yet
        pass

    def run(self, env) -> Tuple[List[Coord], int, int]:
        start: Coord = (0, 0, 0)
        path: List[Coord] = [start]
        total_expansions = 0
        false_visits = 0

        # 1) Build a cost_map from your environment
        #    cost_map[u][v] = env.move_cost(u, v)
        cost_map = {
            (x, y, z): {
                nbr: env.move_cost((x, y, z), nbr)
                for nbr in env.get_neighbors((x, y, z))
            }
            for z in range(env.floors)
            for x in range(env.length)
            for y in range(env.width)
            if not env.is_obstacle((x, y, z))
        }

        # 2) Define your heuristic (Manhattan distance, say)
        def heuristic(u: Coord, v: Coord) -> float:
            return abs(u[0]-v[0]) + abs(u[1]-v[1]) + abs(u[2]-v[2])

        # 3) For each candidate store, instantiate a fresh D* Lite planner
        for goal in env.stores:
            self.planner = DStarLitePlanner(start, goal, heuristic, cost_map)
            # planner.__init__ already runs compute_shortest_path()
            segment = self.planner.get_shortest_path()
            path += segment[1:]           # drop duplicate start
            total_expansions += getattr(self.planner, 'expanded', 0)
            start = goal

            if env.has_item(goal):
                break
            false_visits += 1

        return path, total_expansions, false_visits
