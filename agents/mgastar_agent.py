from interfaces.agents import Agent

class MultiGoalAStarAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner
        self.total_steps = 0
        self.total_expansions = 0
        self.path_cost = 0
        self.total_path_cost = 0
        self.success = False

    def run(self, env, start_node, goal_nodes: list):
        sorted_goals, expanded = self.planner.plan(env, start_node, goal_nodes)

        for result in sorted_goals:
            goal = result["goal"]
            path = result["path"]
            expansions = result.get("expanded", 0)
            cost = result["cost"]

            self.total_steps += len(path)
            self.total_expansions += expansions
            self.path_cost += max(0, len(path) - 1)
            self.total_path_cost += cost

            # print(f"Now heading to: {goal.name} at ({goal.row},{goal.column})")
            # print(f"Path leads to: ({path[-1].row},{path[-1].column})")
            # print(f"Target store is: ({goal.row},{goal.column})")
            # print(f"Has goal item? {'Yes' if goal.has_goal_item else 'No'}")

            if goal.has_goal_item:
                self.success = True
                return path, expansions, goal

        print("WARNING: No reachable store had the goal item.")
        return None, expanded, None  # No path to correct goal
