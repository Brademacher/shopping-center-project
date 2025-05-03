import random
from collections import deque

from interfaces.nodes import Node
from mallcomponents.node_connectivity import * # type: ignore
from nodecomponents.goal_logic import assign_goal_item_to_store
from nodecomponents.stores import Store
from nodecomponents.static_obstacles import Obstacle

class Floor():

    def __init__(self, rows: int, columns: int, f_number: int = 0):
        self.rows = rows
        self.columns = columns
        self.f_number = f_number
        self.start_node = None

        # List of stores on the floor #
        self.perimeter: list[Node] = [] # List to hold perimeter nodes
        self.stores = []  # List to hold store nodes
        self.elevators = [] # List to hold elevator nodes
        self.stairs = [] # List to hold stairs nodes

        # Generating floor grid #
        self.grid = [[Node(i, j, self.f_number) for j in range(self.columns)] for i in range(self.rows)]
        self.build_perimeter_list()

        connect_nodes(self.grid, self.rows, self.columns)
    

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
            and not is_corner(node.row, node.column, self.rows, self.columns)
            and any(n.direction == get_inward_direction(node.row, node.column, self.rows, self.columns)
                    for n in node.get_neighbors())
        ]
        random.shuffle(valid_spots)

        for index, node in enumerate(valid_spots[:count]):
            store = Store(node.row, node.column, self.f_number, name=f"Store-{index}", has_goal_item=False)
            self.grid[node.row][node.column] = store
            self.stores.append(store)

        connect_nodes(self.grid, self.rows, self.columns)


    def place_agent_start(self):
        valid_spots = [
            node for node in self.perimeter
            if node.node_type == "generic"
            and not is_corner(node.row, node.column, self.rows, self.columns)
            and any(n.direction == get_inward_direction(node.row, node.column, self.rows, self.columns)
                    for n in node.get_neighbors())
        ]
        random.shuffle(valid_spots)

        if not valid_spots:
            raise RuntimeError("No valid perimeter node for agent start.")

        self.start_node = valid_spots[0]
        self.start_node.node_type = "start"
        add_inward_neighbor(self.grid, self.start_node, self.rows, self.columns)
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
        viable_nodes = []
        for row in self.grid:
            for node in row:
                if node.node_type == "generic" and node not in self.perimeter:
                    viable_nodes.append(node)

        # Filter out nodes that block store/start entries
        viable_nodes = [
            node for node in viable_nodes
            if not is_blocking_entry(node, lambda r, c: get_inward_direction(r, c, self.rows, self.columns))
        ]

        random.shuffle(viable_nodes)
        placed = 0

        for node in viable_nodes:
            if placed >= count:
                break
            if self.place_single_obstacle(node.row, node.column):
                placed += 1

        return placed


    def place_single_obstacle(self, row: int, column: int):
                # Temporarily place obstacle
        original = self.grid[row][column]
        obstacle = Obstacle(row, column, self.f_number)
        self.grid[row][column] = obstacle

        # Remove this node from its neighbors' neighbor lists (outgoing edges)
        for neighbor_link in original.get_neighbors():
            neighbor = neighbor_link.node
            reverse_dir = {
                "up": "down", "down": "up",
                "left": "right", "right": "left"
            }.get(neighbor_link.direction)
            if reverse_dir:
                neighbor.remove_neighbor(reverse_dir)
                neighbor.add_neighbor(reverse_dir, obstacle)

        # Check connectivity
        if is_fully_connected(self.start_node, self.stores, self.grid):
            return True  # Obstacle placement is valid
        else:
            # Revert obstacle placement and restore neighbor links
            for neighbor_link in original.get_neighbors():
                neighbor = neighbor_link.node
                reverse_dir = {
                    "up": "down", "down": "up",
                    "left": "right", "right": "left"
                }.get(neighbor_link.direction)
                if reverse_dir:
                    neighbor.remove_neighbor(reverse_dir)
                    neighbor.add_neighbor(reverse_dir, original)
            self.grid[row][column] = original 
            return False  # Obstacle placement is invalid


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
                if self.start_node and node == self.start_node:
                    row_str += "[ A ]"
                elif coord in path_coords:
                    row_str += "[ * ]"
                elif node.node_type == "store" and getattr(node, "has_goal_item", False):
                    row_str += "[ G ]"
                elif node.node_type == "store":
                    row_str += "[ S ]"
                elif node.node_type == "obstacle":
                    row_str += "[OOO]"
                elif node.node_type == "generic":
                    row_str += "[   ]"
                elif node.node_type == "elevator":
                    row_str += "[ E ]"
                else:
                    row_str += "[ ? ]"
            print(row_str)


# # TESTING PURPOSES ONLY #
# if __name__ == "__main__":
#     floor = Floor(rows=10, columns=12, f_number=0)

#     floor.place_agent_start()
#     floor.place_stores(count=6)
#     assign_goal_item_to_store(floor.stores)
#     floor.place_obstacles(count=10)

#     floor.print_floor_layout_with_obstacles()

#     print("\nStore Summary:")
#     print(f"\nDEBUG: Store count = {len(floor.stores)}")
#     store_names = [s.name for s in floor.stores]
#     print(f"DEBUG: Unique store names = {set(store_names)}")
#     for store in floor.stores:
#         status = "GOAL ITEM" if store.has_goal_item else "empty"
#         print(f"- {store.name} at ({store.row},{store.column}) → {status}")