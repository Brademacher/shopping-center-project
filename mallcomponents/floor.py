import random
from interfaces.nodes import Node
from nodecomponents.goal_logic import assign_goal_item_to_store
from nodecomponents.stores import Store

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
                if i > 0:
                    self.grid[i][j].add_neighbor("up", self.grid[i - 1][j])
                if i < self.rows - 1:
                    self.grid[i][j].add_neighbor("down", self.grid[i + 1][j])
                if j > 0:
                    self.grid[i][j].add_neighbor("left", self.grid[i][j - 1])
                if j < self.columns - 1:
                    self.grid[i][j].add_neighbor("right", self.grid[i][j + 1])
    
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

        valid_spots = [node for node in self.perimeter if node.node_type == "generic"]
        random.shuffle(valid_spots)

        for index, node in enumerate(valid_spots[:count]):
            store = Store(node.row, node.column, self.f_number, name=f"Store-{index}", has_goal_item=False)
            self.grid[node.row][node.column] = store
            self.stores.append(self.grid[node.row][node.column])

        # 💥 Important: Rebuild neighbor links
        self.connect_nodes()

    def place_agent_start(self):
        """
        Randomly selects a 'generic' node on the perimeter to use as the agent's starting point.
        """
        valid_spots = [node for node in self.perimeter if node.node_type == "generic"]
        random.shuffle(valid_spots)

        if not valid_spots:
            raise RuntimeError("No valid perimeter node for agent start.")

        self.start_node = valid_spots[0]
        self.start_node.node_type = "start"
        print(f"Agent start node set to ({self.start_node.row}, {self.start_node.column})")


# TESTING PURPOSES ONLY #
if __name__ == "__main__":

    floor = Floor(rows=6, columns=8, f_number=0)
    floor.place_agent_start()
    floor.place_stores(count=5)
    assign_goal_item_to_store(floor.stores)

    print("\nFloor Layout:\n")
    for row in floor.grid:
        row_str = ""
        for node in row:
            match node.node_type:
                case "generic":
                    row_str += "[   ]"
                case "store":
                    row_str += "[ G ]" if node.has_goal_item else "[ s ]"
                case "start":
                    row_str += "[ A ]"
                case _:
                    row_str += "[ ? ]"
        print(row_str)

    print("\nStore Summary:")
    for store in floor.stores:
        status = "GOAL ITEM" if store.has_goal_item else "empty"
        print(f"- {store.name} at ({store.row},{store.column}) → {status}")