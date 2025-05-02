import heapq

class PriorityQueue:
    """
    A priority queue that supports updating and removing entries.
    Entries are (key, count, item), where key is a tuple (k1, k2).
    """
    def __init__(self):
        self.heap = []
        self.entry_finder = {}
        self.REMOVED = '<removed>'
        self.counter = 0

    def put(self, item, key):
        # Remove existing entry if present
        if item in self.entry_finder:
            self.remove(item)
        entry = [key, self.counter, item]
        self.counter += 1
        self.entry_finder[item] = entry
        heapq.heappush(self.heap, entry)

    def remove(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED

    def pop(self):
        while self.heap:
            key, count, item = heapq.heappop(self.heap)
            if item is not self.REMOVED:
                del self.entry_finder[item]
                return item, key
        raise KeyError('pop from empty priority queue')

    def top_key(self):
        while self.heap:
            key, count, item = self.heap[0]
            if item is self.REMOVED:
                heapq.heappop(self.heap)
                continue
            return key
        return (float('inf'), float('inf'))

    def empty(self):
        return not bool(self.entry_finder)


class DStarLitePlanner:
    def __init__(self, start, goal, heuristic, cost_map):
        """
        start, goal: tuples (x, y)
        heuristic: function h(u, v) -> float
        cost_map: dict of dicts, cost_map[u][v] = cost of edge u->v
        """
        self.start = start
        self.goal = goal
        self.heuristic = heuristic
        self.cost_map = cost_map

        self.km = 0
        self.rhs = {}
        self.g = {}
        self.open = PriorityQueue()
        self.s_last = start

        # Initialize g and rhs for all nodes
        for u in cost_map:
            self.g[u] = float('inf')
            self.rhs[u] = float('inf')
        self.rhs[goal] = 0

        # Insert goal into queue
        self.open.put(goal, self.calculate_key(goal))
        self.compute_shortest_path()

    def calculate_key(self, u):
        k1 = min(self.g[u], self.rhs[u]) + self.heuristic(self.start, u) + self.km
        k2 = min(self.g[u], self.rhs[u])
        return (k1, k2)

    def neighbors(self, u):
        return self.cost_map.get(u, {}).keys()

    def cost(self, u, v):
        return self.cost_map[u].get(v, float('inf'))

    def update_vertex(self, u):
        if u != self.goal:
            # Update rhs[u] based on successors
            self.rhs[u] = min(
                self.cost(u, s) + self.g[s]
                for s in self.neighbors(u)
            )
        # Remove from queue if present
        if u in self.open.entry_finder:
            self.open.remove(u)
        if self.g[u] != self.rhs[u]:
            self.open.put(u, self.calculate_key(u))

    def compute_shortest_path(self):
        # Continue until top key >= key(start) and start is locally consistent
        while (self.open.top_key() < self.calculate_key(self.start)
               or self.rhs[self.start] != self.g[self.start]):
            u, k_old = self.open.pop()
            k_new = self.calculate_key(u)
            if k_old < k_new:
                # Node's key changed, reinsert
                self.open.put(u, k_new)
            elif self.g[u] > self.rhs[u]:
                # Vertex became consistent
                self.g[u] = self.rhs[u]
                for p in self.neighbors(u):
                    self.update_vertex(p)
            else:
                # Vertex was overconsistent
                g_old = self.g[u]
                self.g[u] = float('inf')
                # Update u and its predecessors
                for p in list(self.neighbors(u)) + [u]:
                    self.update_vertex(p)

    def update_edge(self, u, v, new_cost):
        """
        Call this when the cost of edge u->v changes to new_cost.
        """
        # Update cost_map
        self.cost_map[u][v] = new_cost
        # If undirected, also update reverse
        if v in self.cost_map and u in self.cost_map[v]:
            self.cost_map[v][u] = new_cost

        # Replan from current start
        self.km += self.heuristic(self.s_last, self.start)
        self.s_last = self.start
        self.update_vertex(u)
        self.update_vertex(v)
        self.compute_shortest_path()

    def get_shortest_path(self):
        # 1) Detect “no path” up front
        if self.g.get(self.start, float('inf')) == float('inf'):
            raise ValueError(f"No path found from {self.start} to {self.goal}")

        path = [self.start]
        u = self.start
        visited = {u}

        # 2) Reconstruct, but break cycles
        while u != self.goal:
            # Consider only neighbors with a finite g-value
            candidates = [
                s for s in self.neighbors(u)
                if self.g.get(s, float('inf')) < float('inf')
            ]
            if not candidates:
                raise ValueError(f"Stuck at {u}: no finite‐distance successor.")

            # Pick the successor that matches the D*Lite consistency rule:
            # g[u] == cost(u,s) + g[s]
            # (or, failing that, the one with minimum cost+g)
            next_u = min(
                candidates,
                key=lambda s: self.cost(u, s) + self.g[s]
            )

            # Cycle detection
            if next_u in visited:
                raise ValueError(
                    f"Loop detected during path reconstruction at {next_u}"
                )
            visited.add(next_u)

            path.append(next_u)
            u = next_u

        return path


    # Placeholder for sensing edge cost changes in a real robot
    def sense_changes(self):
        """
        Override or extend to return a list of (u, v, new_cost) when changes are observed.
        """
        return []

    def move_and_replan(self):
        """
        Execute moves from start to goal, replanning when costs change.
        Returns the path taken.
        """
        path = [self.start]
        while self.start != self.goal:
            # Move to best successor
            next_u = min(
                self.neighbors(self.start),
                key=lambda s: self.cost(self.start, s) + self.g[s]
            )
            # Check for any sensed cost changes
            for (u, v, new_cost) in self.sense_changes():
                self.update_edge(u, v, new_cost)
            # Advance
            self.start = next_u
            path.append(self.start)
        return path
