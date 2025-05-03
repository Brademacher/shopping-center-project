from interfaces.agents import Agent

class DStarLiteAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner

        self.path_cost = 0
        self.total_steps = 0
        self.total_expansions = 0
        self.total_path_cost = 0
        self.total_replans = 0
        self.success = False

    def run(self, env, start_node, goal_nodes: list):
        """
        Try each store in goal_nodes until we find the one with the item,
        accumulating all steps, expansions, costs and replans.
        """

        position = start_node    # local “where I am” (avoids shadowing planner.start)
        first    = True

        for goal in goal_nodes:
            if not first:
                self.total_replans += 1
            first = False

            print(f"Planning from ({position.row},{position.column}) "
                f"to ({goal.row},{goal.column})")
            path, expanded = self.planner.plan(env, position, goal)
            if not path:
                continue

            # count the edges traversed
            moves = len(path) - 1
            self.total_steps      += moves
            self.total_expansions += expanded

            # sum up the weights along that path
            cost = 0
            for i in range(moves):
                src, dst = path[i], path[i+1]
                for link in src.get_neighbors():
                    if link.node is dst:
                        cost += link.weight
                        break
            self.total_path_cost += cost

            print(f"Reached ({dst.row},{dst.column}) — moves={moves}, cost={cost}")

            if goal.has_goal_item:
                self.success = True
                return path, expanded

            # “move” the agent and update D*-Lite’s km
            position = path[-1]
            self.planner.km += self.planner.heuristic(self.planner.start, position)

        # none of the stores had the item
        return None, 0


        # start = start_node
        # for goal in goal_nodes:
        #     self.planner.initialize(start, goal)
        #     path, expanded = self.planner.plan(env, start, goal)

        #     if not path:
        #         continue   # couldn’t reach this goal — try the next one

        #     # --- update metrics exactly once per sub-plan ---
        #     moves = len(path) - 1
        #     self.total_steps     += moves
        #     self.total_expansions += expanded

        #     cost = 0
        #     for i in range(moves):
        #         current = path[i]
        #         next = path[i+1]
        #         for link in current.get_neighbors():
        #             if link.node == next:
        #                 cost += link.weight
        #                 break
        #     self.total_path_cost += cost

        #     if goal.has_goal_item:
        #         self.success = True
        #         return path, expanded

        #     # otherwise, “walk” to this non-goal before replanning the next
        #     start = goal
        #     self.planner.km += self.planner.heuristic(self.planner.start, current)

        # # if we fall out of the loop without finding the item:
        # return None, 0
    