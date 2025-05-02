import heapq

class MultiGoalAStarPlanner:
    def __init__(self):
        pass

    def plan(self, env, start_node, goal_nodes):
        import heapq

        open_set = []
        heapq.heappush(open_set, (0, start_node))

        came_from = {}
        g_score = {start_node: 0}
        f_score = {start_node: self.heuristic(start_node, goal_nodes)}

        visited_nodes = set()
        expanded = 0
        reached_goals = {}

        while open_set:
            _, current = heapq.heappop(open_set)
            expanded += 1

            if current in visited_nodes:
                continue
            visited_nodes.add(current)

            if self.is_goal_node(current, goal_nodes):
                # Get the actual goal object (e.g., the Store instance)
                matched_goal = next(
                    (g for g in goal_nodes if g.row == current.row and g.column == current.column and g.f_number == current.f_number),
                    current
                )

                if matched_goal not in reached_goals:
                    path = self.reconstruct_path(came_from, current)
                    reached_goals[matched_goal] = {
                        "goal": matched_goal,
                        "path": path,
                        "cost": g_score[current]
                    }

            for neighbor_link in current.get_neighbors():
                neighbor = neighbor_link.node
                weight = neighbor_link.weight

                if neighbor in visited_nodes:
                    continue

                tentative_g = g_score[current] + weight

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal_nodes)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        # Sort by cost and return
        sorted_goals = sorted(reached_goals.values(), key=lambda x: x["cost"])
        return sorted_goals, expanded


        # Sort results by cost
        sorted_goals = sorted(reached_goals.values(), key=lambda x: x["cost"])
        return sorted_goals, expanded

    def heuristic(self, node, goal_nodes):
        return min(abs(node.row - goal.row) + abs(node.column - goal.column) for goal in goal_nodes)

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]

    def is_goal_node(self, node, goal_nodes):
        return any(
            node.row == g.row and node.column == g.column and node.f_number == g.f_number
            for g in goal_nodes
        )
