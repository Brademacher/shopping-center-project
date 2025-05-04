from interfaces.agents import Agent
from algorithms.mgastar import MultiGoalAStarPlanner

class MultiGoalAStarAgent(Agent):
    def __init__(self, planner=None):
        super().__init__()
        self.planner = planner or MultiGoalAStarPlanner()

    def run(self, env, start_node, goal_nodes: list):
        """
        Run one multi-goal A* from start_node to ALL goal_nodes,
        then accumulate length & cost of each sub-path in ascending
        order until we hit the store with the goal item.
        Returns: (path_to_goal, total_expanded, total_length, total_cost)
        """
        # single planning pass
        sorted_goals, total_expanded = self.planner.plan(
            env, start_node, goal_nodes
        )

        total_length = 0
        total_cost   = 0.0
        final_path   = []
        
        # walk through the sorted results
        for result in sorted_goals:
            path = result["path"]
            cost = result["cost"]
            total_length += len(path)
            total_cost   += cost

            if result["goal"].has_goal_item:
                final_path = path
                break

        return final_path, total_expanded, total_length, total_cost