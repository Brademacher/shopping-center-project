import random

class MallAgent:
    def __init__(self, env, start=(0, 0, 0), planner=None):
        self.env = env
        self.position = start
        self.path = [start]
        self.cost = 0
        self.planner = planner
        self.planned_path = []

        if self.planner:
            self.planned_path = self.planner.plan(env, self.position)
            if self.planned_path:
                self.planned_path.pop(0)  # skip starting point

    def step(self):
        if self.env.goal_reached:
            return False

        if self.planner and self.planned_path:
            x, y, f = self.planned_path.pop(0)
            # Find the cost of the move from neighbors
            for nx, ny, nf, move_cost in self.env.get_neighbors(*self.position):
                if (nx, ny, nf) == (x, y, f):
                    cost = move_cost
                    break
            else:
                cost = 1  # fallback if somehow not found
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