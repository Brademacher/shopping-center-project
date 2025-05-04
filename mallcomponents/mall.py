import random
from mallcomponents.floor import Floor
from mallcomponents.node_connectivity import connect_nodes, is_corner, lock_stair_neighbors
from nodecomponents.elevators import Elevator
from nodecomponents.stairs import Stairs
from nodecomponents.goal_logic import assign_goal_item_to_store

class Mall:
    def __init__(self, num_floors: int, rows: int, columns: int, 
                stores_per_floor: int = 0, obstacles_per_floor: int = 0,
                store_density: float = 0.0, obstacle_density: float = 0.0,
                num_elevators: int = 0, num_stairs: int = 0,
                elevator_density: float = 0.0, stairs_density: float = 0.0):
        
        self.num_floors = num_floors
        self.rows = rows
        self.columns = columns

        nodes_per_floor = rows * columns
        self.nodes_per_floor = nodes_per_floor

        self.stores = stores_per_floor
        self.store_density = store_density

        self.obstacles = obstacles_per_floor
        self.obstacle_density = obstacle_density

        self.num_elevators = num_elevators
        self.elevator_density = elevator_density

        self.num_stairs = num_stairs
        self.stairs_density = stairs_density

        self.floors = []
        self.agent_start_floor = random.randint(0, num_floors - 1)
    
    def build_base_floors(self):
        """Builds the base floors of the mall."""
        for i in range(self.num_floors):
            floor = Floor(rows=self.rows, columns=self.columns, f_number=i)
            self.floors.append(floor)

    def place_agent(self):
        """Places the agent on a random floor."""
        self.floors[self.agent_start_floor].place_agent_start()

    def get_elevator_placement_count(self, floor: Floor):
        """Determines the number of elevators to place in mall."""

        perimeter_size = len(floor.perimeter)

        if self.num_elevators > 0:
            return self.num_elevators
        elif self.elevator_density > 0:
            return int(perimeter_size * self.elevator_density)
        else:
            return int(perimeter_size * 0.05)
        # Default to 5% of the perimeter if no specific count or density is provided

    def place_elevators(self):
        """
        Places elevators at shared (row, col) perimeter locations on all floors.
        """
        base_floor = self.floors[0]
        valid_nodes = []

        # Find perimeter (row, col) positions that are valid on ALL floors
        for node in base_floor.perimeter:
            row, column = node.row, node.column
            if is_corner(row, column, self.rows, self.columns):
                continue

            if all(floor.grid[row][column].node_type == "generic" for floor in self.floors):
                valid_nodes.append((row, column))

        # Determine how many elevators to place using your helper
        elevator_count = self.get_elevator_placement_count(base_floor)
        random.shuffle(valid_nodes)
        selected_nodes = valid_nodes[:elevator_count]

        for i, (e_row, e_column) in enumerate(selected_nodes):
            for floor in self.floors:
                elevator = Elevator(row=e_row, column=e_column, f_number=floor.f_number)
                floor.grid[e_row][e_column] = elevator  
                floor.elevators.append(elevator)

        for floor in self.floors:
            connect_nodes(floor.grid, floor.rows, floor.columns)
            floor.build_perimeter_list()

        # Add vertical neighbors for each elevator exactly once:
        for idx, floor in enumerate(self.floors):
            for elevator in floor.elevators:
                r, c = elevator.row, elevator.column

                # link up to the elevator on the floor above
                if idx < len(self.floors) - 1:
                    above = self.floors[idx + 1].grid[r][c]
                    if not any(link.direction == "up_floor" and link.node is above
                            for link in elevator.get_neighbors()):
                        elevator.add_neighbor("up_floor", above)
                        above.add_neighbor("down_floor", elevator)

                # link down to the elevator on the floor below
                if idx > 0:
                    below = self.floors[idx - 1].grid[r][c]
                    if not any(link.direction == "down_floor" and link.node is below
                            for link in elevator.get_neighbors()):
                        elevator.add_neighbor("down_floor", below)
                        below.add_neighbor("up_floor", elevator)

        # Print to elevator neighbors
        # for i in range(len(self.floors)):
        #     for elev in sorted(self.floors[i].elevators, key=lambda e: (e.row, e.column)):
        #         nbrs = [
        #             (link.direction,
        #             (link.node.row, link.node.column, link.node.f_number))
        #             for link in elev.get_neighbors()
        #         ]
        #         print(f"{elev.name} {nbrs}")
        
        

    def get_stairs_placement_count(self, floor: Floor):
        """Determines the number of stairs to place in mall."""

        perimeter_size = len(floor.perimeter)

        if self.num_stairs > 0:
            return self.num_stairs
        elif self.stairs_density > 0:
            return int(perimeter_size * self.stairs_density)
        else:
            return int(perimeter_size * 0.05)
        # Default to 5% of the perimeter if no specific count or density is provided

    def place_stairs(self):
        """ Place Stairs in interior generic nodes on each floor. """
        for f in range(self.num_floors - 1):
            lower_floor = self.floors[f]
            upper_floor = self.floors[f + 1]
            count = self.get_stairs_placement_count(lower_floor)

            valid_nodes = [
                (row, column)
                for row in range(2, lower_floor.rows - 2)
                for column in range(2, lower_floor.columns - 2)
                if (lower_floor.grid[row][column].node_type == "generic"
                    and upper_floor.grid[row][column + 1].node_type == "generic")
            ]
            random.shuffle(valid_nodes)

            for row, column in valid_nodes[:count]:
                # Place lower stairs
                lower = Stairs(row=row, column=column, f_number=lower_floor.f_number)
                lower_floor.grid[row][column] = lower
                lower_floor.stairs.append(lower)

                # Place upper stairs
                upper = Stairs(row=row, column=column + 1, f_number=upper_floor.f_number)
                upper_floor.grid[row][column + 1] = upper
                upper_floor.stairs.append(upper)

        # Connect stairs on each floor to their neighbors
        for floor in self.floors:
            connect_nodes(floor.grid, floor.rows, floor.columns)
            floor.build_perimeter_list()

        # Add vertical neighbors for each stair exactly once:
        # For each pair of floors, link the stairs on the lower floor to the stairs on the upper floor
        for f in range(self.num_floors - 1):
            lower = self.floors[f]
            upper = self.floors[f+1]
            for low in lower.stairs:
                r, c = low.row, low.column

                # find its matching upper stair
                # is this actually a lower‐end stair?
                # check that on floor f+1 at (r,c+1) we put a Stairs
                if (c+1 < upper.columns
                    and isinstance(upper.grid[r][c+1], Stairs)):
                    up = upper.grid[r][c+1]
                    low.add_neighbor("up_stairs",   up)
                    up.add_neighbor("down_stairs",  low)

        ## Add horizontal neighbors for each stair on the same floor
        # For each floor, link the stairs to their neighbors
        for floor_idx, floor in enumerate(self.floors):
            for stair in floor.stairs:

                r, c = stair.row, stair.column

                if any(l.direction=="up_stairs" for l in stair.get_neighbors()):
                    # lower stair: prune, then inspect its right neighbor
                    lock_stair_neighbors(stair, {"left", "up_stairs"})

                else:
                    # upper stair: prune, then inspect its left neighbor
                    lock_stair_neighbors(stair, {"right", "down_stairs"})
                    

    def get_all_stores(self):
        """Returns a list of all Store nodes across all floors."""
        return [store for floor in self.floors for store in floor.stores]

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

    def get_obstacle_placement_count(self, floor: Floor):
        """"Determines the number of obstacles to place on each floor."""

        viable_node_count = self.nodes_per_floor - len(floor.perimeter)  # Exclude perimeter nodes

        if self.obstacles > 0:
            return self.obstacles
        elif self.obstacle_density > 0:
            return int(viable_node_count * self.obstacle_density)
        else:
            return int(viable_node_count * 0.25)
        # Default to 25% of the viable floor nodes if no specific count or density is provided

    def populate_floors(self):
        globbal_start = self.floors[self.agent_start_floor].start_node
        global_stores = self.get_all_stores()

        for floor in self.floors:
            store_count = self.get_store_placement_count(floor)
            floor.place_stores(count=store_count)

            obstacle_count = self.get_obstacle_placement_count(floor)
            floor.place_obstacles(count=obstacle_count, start=globbal_start, stores=global_stores)

    def run_mall_setup(self):
        """
        Builds the entire mall layout, including floors, stores, and obstacles.
        """
        self.build_base_floors()
        self.place_agent()
        self.place_elevators()
        self.place_stairs()
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
        num_floors=4,
        rows=20,
        columns=20,
        num_elevators= 10
    )

    mall.run_mall_setup()
    mall.print_mall_layout()