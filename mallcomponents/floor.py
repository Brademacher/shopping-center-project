import random
from collections import deque

from interfaces.nodes import Node
from nodecomponents.goal_logic import assign_goal_item_to_store
from nodecomponents.stores import Store
from nodecomponents.static_obstacles import Obstacle

class Floor():

    def __init__(self, rows: int, columns: int, f_number: int = 0, auto_connect: bool = True):
        self.rows = rows
        self.columns = columns
        self.f_number = f_number
        self.start_node = None

        # List of stores on the floor #
        self.perimeter: list[Node] = [] # List to hold perimeter nodes
        self.stores = []  # List to hold store nodes

        # Generating floor grid #
        self.grid = [[Node(i, j, self.f_number) for j in range(self.columns)] for i in range(self.rows)]
        self.build_perimeter_list()

        if auto_connect:
            self.connect_nodes()

    def connect_nodes(self):
        for i in range(self.rows):
            for j in range(self.columns):
                node = self.grid[i][j]

                if i == 0:
                    node.add_neighbor("down", self.grid[i + 1][j])  # top row
                elif i == self.rows - 1:
                    node.add_neighbor("up", self.grid[i - 1][j])    # bottom row
                elif j == 0:
                    node.add_neighbor("right", self.grid[i][j + 1]) # left column
                elif j == self.columns - 1:
                    node.add_neighbor("left", self.grid[i][j - 1])  # right column
                else:
                    # inner node — fully connected
                    node.add_neighbor("up", self.grid[i - 1][j])
                    node.add_neighbor("down", self.grid[i + 1][j])
                    node.add_neighbor("left", self.grid[i][j - 1])
                    node.add_neighbor("right", self.grid[i][j + 1])
    
    def build_perimeter_list(self):
        """
        Populates self.perimeter with all Node objects along the outer edge of the grid.
        """
        self.perimeter.clear()

        for j in range(self.columns):
            self.perimeter.append(self.grid[0][j])                  # top row
            self.perimeter.append(self.grid[self.rows - 1][j])      # bottom row
        for i in range(1, self.rows - 1):
            self.perimeter.append(self.grid[i][0])                  # left col
            self.perimeter.append(self.grid[i][self.columns - 1])   # right col

    def get_node(self, row: int, column: int) -> Node:
        if 0 <= row < self.rows and 0 <= column < self.columns:
            return self.grid[row][column]
        else:
            raise IndexError("Node coordinates out of bounds")

    def place_stores(self, count: int):

        valid_spots = [
            node for node in self.perimeter
            if node.node_type == "generic"
            and not self.is_corner(node.row, node.column)
            and any(n.direction == self.get_inward_direction(node.row, node.column) for n in node.get_neighbors())
        ]       
        random.shuffle(valid_spots)

        for index, node in enumerate(valid_spots[:count]):
            store = Store(node.row, node.column, self.f_number, name=f"Store-{index}", has_goal_item=False)
            self.grid[node.row][node.column] = store
            self.stores.append(store)

        # 💥 Important: Rebuild neighbor links
        self.connect_nodes()

    def place_agent_start(self):
        """
        Randomly selects a 'generic' node on the perimeter to use as the agent's starting point.
        """
        valid_spots = [
            node for node in self.perimeter
            if node.node_type == "generic"
            and not self.is_corner(node.row, node.column)
            and any(n.direction == self.get_inward_direction(node.row, node.column) for n in node.get_neighbors())
        ]
        random.shuffle(valid_spots)

        if not valid_spots:
            raise RuntimeError("No valid perimeter node for agent start.")

        # Reconnect inward-facing neighbor in case of disconnection
        self.start_node = valid_spots[0]
        self.start_node.node_type = "start"
        self.add_inward_neighbor(self.start_node)
        print(f"Agent start node set to ({self.start_node.row}, {self.start_node.column})")

    def place_obstacles(self, count: int):
        """
        Randomly places static obstacles that block movement.
        Constraints:
        - Cannot be on the perimeter
        - Cannot be directly in front of a store or start
        - Must not fully block access to all goals or the agent
        """

       # Gather viable candidate nodes
        viable_nodes = [
            node for row in self.grid for node in row
            if node.node_type == "generic" and node not in self.perimeter
        ]

        # Filter out nodes that block store/start entries
        viable_nodes = [
            node for node in viable_nodes
            if not is_blocking_entry(node, self.get_inward_direction)
        ]

        random.shuffle(viable_nodes)
        placed = 0

        for node in viable_nodes:
            if placed >= count:
                break

            # Temporarily place obstacle
            original = self.grid[node.row][node.column]
            self.grid[node.row][node.column] = Obstacle(node.row, node.column, self.f_number)

            if self.is_fully_connected():
                placed += 1
            else:
                self.grid[node.row][node.column] = original  # Revert if it breaks connectivity

    def add_inward_neighbor(self, node):
        """
        Adds the inward-facing neighbor to a perimeter node.
        Assumes the node is on the perimeter and not in a corner.
        """
        inward_dir = self.get_inward_direction(node.row, node.column)
        if not inward_dir:
            return  # Skip if it's a corner or invalid position

        r, c = node.row, node.column
        neighbor = (
            self.grid[r + 1][c] if inward_dir == "down" else
            self.grid[r - 1][c] if inward_dir == "up" else
            self.grid[r][c + 1] if inward_dir == "right" else
            self.grid[r][c - 1]
        )
        node.neighbors.clear()  # Optional: ensure no old neighbors remain
        node.add_neighbor(inward_dir, neighbor)

    def get_inward_direction(self, row, col):
        if row == 0: return "down"
        if row == self.rows - 1: return "up"
        if col == 0: return "right"
        if col == self.columns - 1: return "left"
        return None
    
    def is_corner(self, row, col):
        return (
            (row == 0 and col == 0) or
            (row == 0 and col == self.columns - 1) or
            (row == self.rows - 1 and col == 0) or
            (row == self.rows - 1 and col == self.columns - 1)
        )
    
    def is_fully_connected(self):
        """
        Uses BFS to ensure all stores are reachable from the start node.
        Returns True if all are reachable, False otherwise.
        """
        if not self.start_node or not self.stores:
            return True  # Nothing to validate

        visited = set()
        queue = deque([self.start_node])
        visited.add((self.start_node.row, self.start_node.column, self.start_node.f_number))

        while queue:
            current = queue.popleft()

            for neighbor_link in current.get_neighbors():
                neighbor = neighbor_link.node
                key = (neighbor.row, neighbor.column, neighbor.f_number)

                if key not in visited and neighbor.node_type != "obstacle":
                    visited.add(key)
                    queue.append(neighbor)

        # Final check
        for store in self.stores:
            key = (store.row, store.column, store.f_number)
            if key not in visited:
                return False

        return True
    
    def print_floor_layout_with_obstacles(self, path_nodes=None):
        """
        Prints the floor with agent path included.
        path_nodes: optional list of nodes the agent path includes.
        """
        path_coords = set((n.row, n.column, n.f_number) for n in path_nodes) if path_nodes else set()

        print("\nFloor Layout with Obstacles:\n")
        for row in self.grid:
            row_str = ""
            for node in row:
                coord = (node.row, node.column, node.f_number)
                if node == self.start_node:
                    row_str += "[ A ]"
                elif coord in path_coords:
                    row_str += "[ * ]"
                elif node.node_type == "store" and getattr(node, "has_goal_item", False):
                    row_str += "[ G ]"
                elif node.node_type == "store":
                    row_str += "[ s ]"
                elif node.node_type == "obstacle":
                    row_str += "[ o ]"
                elif node.node_type == "generic":
                    row_str += "[   ]"
                else:
                    row_str += "[ ? ]"
            print(row_str)


    
def is_blocking_entry(node, inward_direction_func):
    """
    Checks if a node would block entry to a store or start node by occupying the cell
    directly in front of its inward-facing neighbor.
    """
    for neighbor_link in node.get_neighbors():
        neighbor = neighbor_link.node
        direction = neighbor_link.direction

        if neighbor.node_type in ("store", "start"):
            inward = inward_direction_func(neighbor.row, neighbor.column)
            if direction == inward:
                return True
    return False

# TESTING PURPOSES ONLY #
if __name__ == "__main__":
    from mallcomponents.floor import Floor
    from nodecomponents.goal_logic import assign_goal_item_to_store

    floor = Floor(rows=10, columns=12, f_number=0)

    floor.place_agent_start()
    floor.place_stores(count=6)
    assign_goal_item_to_store(floor.stores)
    floor.place_obstacles(count=10)

    floor.print_floor_layout_with_obstacles()

    print("\nStore Summary:")
    print(f"\nDEBUG: Store count = {len(floor.stores)}")
    store_names = [s.name for s in floor.stores]
    print(f"DEBUG: Unique store names = {set(store_names)}")
    for store in floor.stores:
        status = "GOAL ITEM" if store.has_goal_item else "empty"
        print(f"- {store.name} at ({store.row},{store.column}) → {status}")