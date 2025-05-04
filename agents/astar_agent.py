from interfaces.agents import Agent
from algorithms.astar import AStarPlanner

class AStarAgent(Agent):
    def __init__(self, planner=None):
        super().__init__()
        self.planner = planner or AStarPlanner()

    def run(self, env, start_node, goal_nodes: list):
        """
        Repeatedly A* from the same start_node to each store
        in ascending manhattan order, accumulating totals, until
        we hit the store with the goal item.
        Returns: (final_path, total_expanded, total_length, total_cost)
        """
        # sort stores by straight‐line (manhattan) distance from the start
        remaining = sorted(
            goal_nodes,
            key=lambda s: abs(start_node.row - s.row) + abs(start_node.column - s.column)
        )

        total_expanded = 0
        total_length   = 0
        total_cost     = 0.0

        for target in remaining:
            path, expanded = self.planner.plan(env, start_node, target)
            total_expanded += expanded

            if not path:
                # safety check
                continue

            # accumulate the length and cost of this sub‐path
            sub_length = len(path)
            sub_cost = 0.0
            
            # sum up the actual edge‐weights
            for a, b in zip(path, path[1:]):
                for link in a.get_neighbors():
                    if link.node is b:
                        sub_cost += link.weight
                        break

            total_length += sub_length
            total_cost   += sub_cost

            if getattr(target, "has_goal_item", False):
                return path, total_expanded, total_length, total_cost

        return [], total_expanded, total_length, total_cost
