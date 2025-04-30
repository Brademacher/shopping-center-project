import random

class MallAgent:
    def __init__(self, env, start=(0, 0, 0), planner=None):
        self.env = env
        self.position = start
        self.path = [start]
        self.cost = 0
        self.planner = planner  # A* planner or None
        self.planned_path = []  # Filled if planner is used

    def step(self):
        if self.planner:
            if not self.planned_path:
                self.planned_path = self.planner.plan(self.env, self.position)
            if not self.planned_path:
                return False  # No path found
            next_move = self.planned_path.pop(0)
            x, y, f = next_move
            cost = 1  # or look up actual cost
        else:
            # Fallback: random
            neighbors = self.env.get_neighbors(*self.position)
            if not neighbors:
                return False
            x, y, f, cost = random.choice(neighbors)

        self.position = (x, y, f)
        self.path.append(self.position)
        self.cost += cost
        self.env.visit_store(x, y, f)
        return not self.env.goal_reached