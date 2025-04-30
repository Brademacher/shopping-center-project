import heapq

class AStarPlanner:
    def __init__(self, goal_store_location):
        self.goal = goal_store_location  # (x, y, f)

    def heuristic(self, a, b):
        # Manhattan distance including floor difference
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def plan(self, env, start):
        MAX_NODES = 10000  # optional safety cap
        steps = 0

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier and steps < MAX_NODES:
            _, current = heapq.heappop(frontier)
            steps += 1

            if current == self.goal:
                # Reconstruct path
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for nx, ny, nf, step_cost in env.get_neighbors(*current):
                next_pos = (nx, ny, nf)
                new_cost = cost_so_far[current] + step_cost

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(next_pos, self.goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        return []  # No path found or capped