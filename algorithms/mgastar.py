import heapq
from typing import List, Tuple, Set, Optional

Pos = Tuple[int, int, int]

class MultiGoalAStarPlanner:
    def __init__(self, goals: List[Pos]):
        self.goals = set(goals)

    def heuristic(self, a: Pos, b: Pos) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def choose_next_goal(self, current: Pos, visited: Set[Pos]) -> Optional[Pos]:
        """Pick nearest unvisited goal by heuristic."""
        unvisited = [g for g in self.goals if g not in visited]
        if not unvisited:
            return None
        return min(unvisited, key=lambda g: self.heuristic(current, g))

    def astar(self, start: Pos, goal: Pos, env) -> Tuple[List[Pos], float]:
        """Public wrapper that uses A* to compute path from start to goal."""
        return self._astar(env, start, goal)

    def _astar(self, env, start: Pos, goal: Pos) -> Tuple[List[Pos], float]:
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == goal:
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1], cost_so_far[goal]

            for nx, ny, nf, step_cost in env.get_neighbors(*current):
                next_pos = (nx, ny, nf)
                new_cost = cost_so_far[current] + step_cost
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        return [], float('inf')  # fail case
