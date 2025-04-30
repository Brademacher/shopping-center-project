import heapq

class DStarLitePlanner:
    def __init__(self, goal):
        self.goal = goal  # (x, y, f)
        self.km = 0
        self.rhs = {}
        self.g = {}
        self.U = []
        self.s_last = None

    def heuristic(self, a, b):
        # Manhattan distance including floor difference
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    def calculate_key(self, s, start):
        min_val = min(self.g.get(s, float('inf')), self.rhs.get(s, float('inf')))
        return (min_val + self.heuristic(start, s) + self.km, min_val)

    def initialize(self, env, start):
        self.rhs[self.goal] = 0
        self.g[self.goal] = float('inf')
        self.U = []
        heapq.heappush(self.U, (self.calculate_key(self.goal, start), self.goal))
        self.s_last = start

    def update_vertex(self, u, env, start):
        if u != self.goal:
            min_rhs = float('inf')
            for nx, ny, nf, cost in env.get_neighbors(*u):
                s = (nx, ny, nf)
                min_rhs = min(min_rhs, self.g.get(s, float('inf')) + cost)
            self.rhs[u] = min_rhs
        self.U = [entry for entry in self.U if entry[1] != u]
        heapq.heapify(self.U)
        if self.g.get(u, float('inf')) != self.rhs.get(u, float('inf')):
            heapq.heappush(self.U, (self.calculate_key(u, start), u))

    def compute_shortest_path(self, env, start):
        while self.U:
            k_old, u = heapq.heappop(self.U)
            k_new = self.calculate_key(u, start)
            if k_old < k_new:
                heapq.heappush(self.U, (k_new, u))
            elif self.g.get(u, float('inf')) > self.rhs.get(u, float('inf')):
                self.g[u] = self.rhs[u]
                for nx, ny, nf, cost in env.get_neighbors(*u):
                    s = (nx, ny, nf)
                    self.update_vertex(s, env, start)
            else:
                self.g[u] = float('inf')
                self.update_vertex(u, env, start)
                for nx, ny, nf, cost in env.get_neighbors(*u):
                    s = (nx, ny, nf)
                    self.update_vertex(s, env, start)

    def plan(self, env, start):
        self.initialize(env, start)
        self.compute_shortest_path(env, start)
        path = []
        current = start

        if self.g.get(current, float('inf')) == float('inf'):
            return []

        path.append(current)
        while current != self.goal:
            min_cost = float('inf')
            next_node = None
            for nx, ny, nf, cost in env.get_neighbors(*current):
                s = (nx, ny, nf)
                total_cost = self.g.get(s, float('inf')) + cost
                if total_cost < min_cost:
                    min_cost = total_cost
                    next_node = s
            if next_node is None:
                return []
            current = next_node
            path.append(current)

        return path