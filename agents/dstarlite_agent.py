import random

class DStarLiteAgent:
    def __init__(self, env, planner=None, start=(0, 0, 0)):
        self.env = env
        self.position = start
        self.path = [start]
        self.cost = 0
        self.step_count = 0
        self.max_steps = 100000
        self.planner = planner
        self.planned_path = []

        # If planner is provided externally, use it; otherwise, build from goal
        if self.planner is None:
            goal_index = env.goal_store_trigger_index
            if goal_index is not None and 0 <= goal_index < len(env.stores):
                goal = env.stores[goal_index]
                from algorithms.dstarlite import DStarLitePlanner
                self.planner = DStarLitePlanner(goal)

        if self.planner:
            self.planned_path = self.planner.plan(env, self.position)
            if self.planned_path:
                self.planned_path.pop(0)  # Remove the current position

    def step(self):
        if self.env.goal_reached or self.step_count > self.max_steps:
            return False

        self.step_count += 1

        if self.planned_path:
            x, y, f = self.planned_path.pop(0)
            for nx, ny, nf, move_cost in self.env.get_neighbors(*self.position):
                if (nx, ny, nf) == (x, y, f):
                    cost = move_cost
                    break
            else:
                cost = 1  # fallback cost if not matched
        else:
            neighbors = self.env.get_neighbors(*self.position)
            if not neighbors:
                return False
            x, y, f, cost = random.choice(neighbors)

        self.position = (x, y, f)
        self.path.append(self.position)
        self.cost += cost
        self.env.visit_store(x, y, f)

        return not self.env.goal_reached
