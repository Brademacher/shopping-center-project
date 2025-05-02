from interfaces.agents import Agent
from algorithms.astar import AStarPlanner
from nodecomponents.stores import Store

class AStarAgent(Agent):
    def __init__(self, planner):
        super().__init__()
        self.planner = planner
        self.visited_stores = set()

    def run(self, env, start_node, goal_nodes: list):
        current = start_node
        path_taken = []
        total_expanded = 0
        remaining_stores = goal_nodes.copy()

        while remaining_stores:
            # Step 1: Choose nearest unvisited store
            remaining_stores.sort(
                key=lambda s: abs(current.row - s.row) + abs(current.column - s.column)
            )
            target = remaining_stores[0]
            print(f"Now heading to: {target.name} at ({target.row},{target.column})")

            # Step 2: A* to target
            path, expanded = self.planner.plan(env, current, target)
            total_expanded += expanded

            if not path:
                print(f"WARNING: No path found to {target.name} at ({target.row},{target.column})")
                self.visited_stores.add(target)
                remaining_stores = [s for s in remaining_stores if s not in self.visited_stores]
                continue

            total_expanded += expanded

            if path_taken:
                path_taken.extend(path[1:])
            else:
                path_taken.extend(path)

            print(f"Path leads to: ({path[-1].row},{path[-1].column})")
            print(f"Target store is: ({target.row},{target.column})")
            print(f"Has goal item? {target.has_goal_item}")

            if target.has_goal_item:
                return path_taken, total_expanded

            self.visited_stores.add(target)
            remaining_stores = [s for s in remaining_stores if s not in self.visited_stores]
            current = target
        
        print("Agent failed to reach any store with the goal item.")
        return path_taken, total_expanded