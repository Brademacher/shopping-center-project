from algorithms.mgastar import MultiGoalAStarPlanner

class MultiGoalAStarAgent:
    def __init__(self):
        self.planner = MultiGoalAStarPlanner()

    def run(self, env):
        start = (0, 0, 0)

        path, exp = self.planner.plan(env, start, env.stores)

        # Determine how many stores appear on the final path
        visited = [s for s in env.stores if s in path]
        false_visits = max(0, len(visited) - 1)          # last one has the item

        return path, exp, false_visits
