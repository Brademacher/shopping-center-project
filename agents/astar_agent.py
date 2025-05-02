from interfaces.agents import Agent

class AStarAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner

    def run(self, env, start_node, goal_nodes):
        goal = goal_nodes[0]
        