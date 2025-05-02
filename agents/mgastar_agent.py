from interfaces.agents import Agent

class MultiGoalAStarAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner

    def run(self, env, start_node, goal_nodes: list):
        sorted_goals, expanded = self.planner.plan(env, start_node, goal_nodes)

        for result in sorted_goals:
            goal = result["goal"]
            path = result["path"]

            print(f"Now heading to: {goal.name} at ({goal.row},{goal.column})")
            print(f"Path leads to: ({path[-1].row},{path[-1].column})")
            print(f"Target store is: ({goal.row},{goal.column})")
            print(f"Has goal item? {'Yes' if goal.has_goal_item else 'No'}")

            if goal.has_goal_item:
                return path, expanded

        print("WARNING: No reachable store had the goal item.")
        return None  # No path to correct goal
