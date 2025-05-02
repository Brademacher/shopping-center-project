import heapq

class AStarPlanner:
    def __init__(self):
        pass

    def plan(self, env, start_node, goal_node):
        priority_queue = []  # ← open_set renamed
        heapq.heappush(priority_queue, (0, start_node))

        came_from = {}
        g_score = {start_node: 0}
        f_score = {start_node: self.heuristic(start_node, goal_node)}

        visited_nodes = set()  # ← closed_set renamed
        expanded = 0

        while priority_queue:
            _, current = heapq.heappop(priority_queue)
            expanded += 1

            if current == goal_node:
                return self.reconstruct_path(came_from, current), expanded

            visited_nodes.add(current)

            for neighbor_link in current.get_neighbors():
                neighbor = neighbor_link.node
                weight = neighbor_link.weight

                if neighbor in visited_nodes:
                    continue

                tentative_g = g_score[current] + weight

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal_node)
                    heapq.heappush(priority_queue, (f_score[neighbor], neighbor))

        return [], expanded  # no path found

    def heuristic(self, node_a, node_b):
        return abs(node_a.row - node_b.row) + abs(node_a.column - node_b.column)

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
