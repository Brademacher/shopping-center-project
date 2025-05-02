import heapq

class DStarLitePlanner:
    def __init__(self):
        self.km = 0  # heuristic offset
        self.rhs = {}  # one-step lookahead values
        self.g = {}    # actual path cost values
        self.U = []    # priority queue
        self.start = None
        self.goal = None

    def initialize(self, start_node, goal_node):
        self.start = start_node
        self.goal = goal_node

        self.rhs[goal_node] = 0
        self.g[goal_node] = float('inf')
        self.g[start_node] = float('inf')
        self.rhs[start_node] = float('inf')

        heapq.heappush(self.U, (self.calculate_key(goal_node), goal_node))

    def calculate_key(self, node):
        g_rhs = min(self.g.get(node, float('inf')), self.rhs.get(node, float('inf')))
        return (g_rhs + self.heuristic(self.start, node) + self.km, g_rhs)

    def heuristic(self, node_a, node_b):
        return abs(node_a.row - node_b.row) + abs(node_a.column - node_b.column)

    def update_vertex(self, u):
        if u != self.goal:
            self.rhs[u] = min(
                [
                    neighbor.weight + self.g.get(neighbor.node, float('inf'))
                    for neighbor in u.get_neighbors()
                ]
            )
        if u in [n for _, n in self.U]:
            self.U = [(k, n) for k, n in self.U if n != u]
            heapq.heapify(self.U)
        if self.g.get(u, float('inf')) != self.rhs.get(u, float('inf')):
            heapq.heappush(self.U, (self.calculate_key(u), u))

    def compute_shortest_path(self):
        while self.U:
            k_old, u = heapq.heappop(self.U)
            k_new = self.calculate_key(u)

            if k_old < k_new:
                heapq.heappush(self.U, (k_new, u))
            elif self.g.get(u, float('inf')) > self.rhs.get(u, float('inf')):
                self.g[u] = self.rhs[u]
                for neighbor in u.get_neighbors():
                    self.update_vertex(neighbor.node)
            else:
                self.g[u] = float('inf')
                self.update_vertex(u)
                for neighbor in u.get_neighbors():
                    self.update_vertex(neighbor.node)

    def plan(self, env, start_node, goal_node):
        self.initialize(start_node, goal_node)
        self.compute_shortest_path()

        # Reconstruct path from start to goal
        current = start_node
        path = [current]

        while current != goal_node:
            neighbors = current.get_neighbors()
            if not neighbors:
                return []  # no path found
            current = min(
                neighbors,
                key=lambda n: self.g.get(n.node, float('inf')) + n.weight
            ).node
            path.append(current)

        return path
