import random
from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store

class Mall:
    def __init__(self, num_floors: int, rows: int, columns: int, 
                stores_per_floor: int = 0, obstacles_per_floor: int = 0,
                store_density: float = 0.0, obstacle_density: float = 0.0):
        
        self.num_floors = num_floors
        self.rows = rows
        self.columns = columns

        nodes_per_floor = rows * columns
        self.nodes_per_floor = nodes_per_floor

        self.stores = stores_per_floor
        self.store_density = store_density

        self.obstacles = obstacles_per_floor
        self.obstacle_density = obstacle_density

        self.floors = []
        self.agent_start_floor = random.randint(0, num_floors - 1)

        self.build_base_floors()
        self.place_agent()
    
    def build_base_floors(self):
        """Builds the base floors of the mall."""
        for i in range(self.num_floors):
            floor = Floor(rows=self.rows, columns=self.columns, f_number=i)
            self.floors.append(floor)

    def place_agent(self):
        """Places the agent on a random floor."""
        self.floors[self.agent_start_floor].place_agent_start()

    def get_all_stores(self):
        """Returns a list of all Store nodes across all floors."""
        return [store for floor in self.floors for store in floor.stores]

    def get_obstacle_placement_count(self, floor: Floor):
        """"Determines the number of obstacles to place on each floor."""

        viable_node_count = self.nodes_per_floor - len(floor.perimeter)  # Exclude perimeter nodes

        if self.obstacles > 0:
            return self.obstacles
        elif self.obstacle_density > 0:
            return int(viable_node_count * self.obstacle_density)
        else:
            return int(viable_node_count * 0.3)
        # Default to 30% of the viable floor nodes if no specific count or density is provided

    def get_store_placement_count(self, floor: Floor):
        """Determines the number of stores to place on each floor."""

        perimeter_size = len(floor.perimeter)

        if self.stores > 0:
            return self.stores
        elif self.store_density > 0:
            return int(perimeter_size * self.store_density)
        else:
            return int(perimeter_size * 0.2)
        # Default to 20% of the floor if no specific count or density is provided

    def populate_floors(self):
        for floor in self.floors:
            store_count = self.get_store_placement_count(floor)
            obstacle_count = self.get_obstacle_placement_count(floor)
            floor.place_stores(count=store_count)

        ###### Temporary: Place obstacles only on agent start floor ######
            if floor.f_number == self.agent_start_floor: 
                floor.place_obstacles(count=obstacle_count)

    def run_mall_setup(self):
        """
        Builds the entire mall layout, including floors, stores, and obstacles.
        """
        self.populate_floors()
        assign_goal_item_to_store(self.get_all_stores())

    def print_mall_layout(self):
        """
        Prints the layout of each floor in the mall, including obstacles,
        stores, and agent start (but no path).
        """
        print("\n=== Mall Layout ===\n")
        for floor in self.floors:
            print(f"\n--- Floor {floor.f_number} ---")
            floor.print_floor_layout_with_obstacles()



### FOR TESTING PURPOSES ONLY ###
if __name__ == "__main__":
    # Create a mall with either store count or density (can mix or swap)
    mall = Mall(
        num_floors=3,
        rows=10,
        columns=12,
    )

    mall.run_mall_setup()
    mall.print_mall_layout()