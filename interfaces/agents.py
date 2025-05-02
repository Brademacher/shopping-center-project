class Agent:
    def __init__(self):
        self.agent_pos = []
        self.expanded_nodes = 0

    def run(self, env, start_node, goal_nodes):
            raise NotImplementedError