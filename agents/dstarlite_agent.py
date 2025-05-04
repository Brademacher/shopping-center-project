from interfaces.agents import Agent

class DStarLiteAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner

    def run(self, env, start_node, goal_nodes: list):
        assert len(goal_nodes) == 1, "D* Lite currently supports a single goal."
        goal_node = goal_nodes[0]

        print(f"Planning path from ({start_node.row}, {start_node.column}) to ({goal_node.row}, {goal_node.column})")
        path, expanded = self.planner.plan(env, start_node, goal_node)

        if path:
            print(f"D* Lite path found. Path length: {len(path)}")
            return path, expanded  # using path length as an approximate expansion metric for now
        else:
            print("No path found.")
            return None