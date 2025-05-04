from interfaces.agents import Agent
from utils.path       import compute_path_cost

class DStarLiteAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner

    def run(self, env, start_node, goal_nodes: list):
        
        assert goal_nodes, "Need at least one goal"

        # 1) sort all the stores once
        remaining = sorted(
            goal_nodes,
            key=lambda s: abs(start_node.row - s.row)
                        + abs(start_node.column - s.column)
        )

        total_expanded = 0
        total_length   = 0
        total_cost     = 0.0
        final_path     = []

        # 2) loop until we find the store with the item
        for target in remaining:
            path, expanded = self.planner.plan(env, start_node, target)
            total_expanded += expanded

            if not path:
                # (shouldn't happen if your 3D‐connectivity guard is solid)
                continue

            sub_length = len(path)
            sub_cost   = compute_path_cost(path)

            total_length += sub_length
            total_cost   += sub_cost

            if getattr(target, "has_goal_item", False):
                final_path = path
                break

        return final_path, total_expanded, total_length, total_cost