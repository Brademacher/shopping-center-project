import heapq
from collections import defaultdict

class DStarLitePlanner:
    def __init__(self):
        self.km = 0                # heuristic
        self.rhs = {}              # one-step lookahead values
        self.g   = {}              # current best path values
        self.U   = []              # priority queue of (key, node)
        self.start = None
        self.goal  = None
        self.expanded = 0          # *** correct expansion count ***

    def initialize(self, start_node, goal_node):
        # reset everything for a fresh run
        self.start = start_node
        self.goal  = goal_node
        self.km    = 0
        self.expanded = 0

        self.rhs.clear()
        self.g.clear()
        self.U.clear()

        # goal’s one-step cost is 0; all others inf
        self.rhs[goal_node] = 0
        self.g[goal_node]   = float('inf')
        self.g[start_node]  = float('inf')
        self.rhs[start_node]= float('inf')

        # seed the queue with the goal
        heapq.heappush(self.U, (self.calculate_key(goal_node), goal_node))

    def calculate_key(self, node):
        g_rhs = min(self.g.get(node, float('inf')),
                    self.rhs.get(node, float('inf')))
        return (g_rhs + self.heuristic(self.start, node) + self.km,
                g_rhs)

    def heuristic(self, a, b):
        return abs(a.row - b.row) + abs(a.column - b.column)

    def update_vertex(self, u):
        if u != self.goal:
            # one-step lookahead: min over neighbors
            self.rhs[u] = min(
                link.weight + self.g.get(link.node, float('inf'))
                for link in u.get_neighbors()
            )
        # remove u from U if it’s in there
        self.U = [(k,n) for k,n in self.U if n is not u]
        heapq.heapify(self.U)

        # re-insert if g ≠ rhs
        if self.g.get(u, float('inf')) != self.rhs.get(u, float('inf')):
            heapq.heappush(self.U, (self.calculate_key(u), u))

    def compute_shortest_path(self):
        # keep going until queue is empty (static run)
        while self.U:
            k_old, u = heapq.heappop(self.U)
            # ** count this as one expansion **
            self.expanded += 1

            k_new = self.calculate_key(u)
            if k_old < k_new:
                # key changed, push back
                heapq.heappush(self.U, (k_new, u))

            elif self.g.get(u, float('inf')) > self.rhs.get(u, float('inf')):
                # improve g to match rhs
                self.g[u] = self.rhs[u]
                # propagate changes
                for link in u.get_neighbors():
                    self.update_vertex(link.node)

            else:
                # make g infinite and propagate
                self.g[u] = float('inf')
                self.update_vertex(u)
                for link in u.get_neighbors():
                    self.update_vertex(link.node)

    def plan(self, env, start_node, goal_node):
        # Reset
        self.initialize(start_node, goal_node)
        # Build the full shortest‐path tree (static case)
        self.compute_shortest_path()
        # Walk it out
        path = self.reconstruct_path(start_node, goal_node)
        return path, self.expanded

    def reconstruct_path(self, start_node, goal_node):
        path = [start_node]
        current = start_node
        while current is not goal_node:
            # choose neighbor minimizing g[nbr]+cost
            candidates = [
                link for link in current.get_neighbors()
                if self.g.get(link.node, float('inf')) < float('inf')
            ]
            if not candidates:
                return []    # no path
            current = min(
                candidates,
                key=lambda link: self.g[link.node] + link.weight
            ).node
            path.append(current)
        return path