import random
from mallcomponents.floor import Floor
from mallcomponents.node_connectivity import connect_nodes, is_corner, add_elevator_vertical_neighbors, update_stair_neighbors
from nodecomponents.elevators import Elevator
from nodecomponents.stairs import Stairs
from nodecomponents.goal_logic import assign_goal_item_to_store

############################       For Printing Purposes      ###################################
from PIL import Image, ImageDraw, ImageFont

def save_layout_as_png(text: str, filename: str = "mall_layout.png", font_size: int = 16):
    try:
        font = ImageFont.truetype("cour.ttf", font_size)  # Windows
    except:
        font = ImageFont.load_default()
        print("Warning: fallback font may not be truly monospaced.")

    lines = text.split('\n')
    padding = 20

    # Estimate char size using getbbox
    bbox = font.getbbox("M")  # monospaced sample character
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]

    max_line_length = max(len(line) for line in lines)

    img_width = padding * 2 + char_width * max_line_length
    img_height = padding * 3 + (5 + char_height) * len(lines) + 10

    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    for i, line in enumerate(lines):
        spacing = 5
        y = padding + i * (char_height + spacing)
        draw.text((padding, y), line, font=font, fill="black")

    image.save(filename)
    print(f"✅ Layout image saved: {filename}")
##############################################################################################

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
        # grab the one start node (on whatever floor the agent began)
        start = self.floors[self.agent_start_floor].start_node

        # grab all of the stores on all floors
        all_stores = self.get_all_stores()

        for floor in self.floors:
            # place stores as before
            store_count = self.get_store_placement_count(floor)
            floor.place_stores(count=store_count)

            obstacle_count = self.get_obstacle_placement_count(floor)
            floor.place_obstacles(
                count=obstacle_count,
                all_stores=all_stores,
                start_node=start
            )

    def run_mall_setup(self):
        """ Builds the entire mall layout, including floors, stores, and obstacles."""
        self.build_base_floors()
        self.place_agent()
        self.place_elevators()
        self.place_stairs()

        for floor in self.floors:
            connect_nodes(floor.grid, floor.rows, floor.columns)
            floor.build_perimeter_list()

        self.populate_floors()
        assign_goal_item_to_store(self.get_all_stores())

        add_elevator_vertical_neighbors(self.floors)
        update_stair_neighbors(self.floors)

    def print_mall_layout(self, to_file = None):

        center_width = self.columns * 5
        lines = []

        lines.append(centered("=== Mall Layout ===", center_width))
        for floor in self.floors:
            lines.append("\n" + centered(f"--- Floor {floor.f_number + 1} ---", center_width))
            lines.extend(floor.print_floor_layout())

        # Add legend
        lines.append("\n" + "-" * 72)
        lines.append("Key".center(72))
        lines.append(f"{'[ A ]':<10} {'Agent Start':<15} {'[ E ]':<10} {'Elevator':<15}")
        lines.append(f"{'[ ^ ]':<10} {'Stairs Up':<15} {'[ v ]':<10} {'Stairs Down':<15}")
        lines.append(f"{'[ S ]':<10} {'Store':<15} {'[ G ]':<10} {'Goal Store':<15}")
        lines.append(f"{'[ X ]':<10} {'Obstacle':<15} {'[   ]':<10} {'Traversal Space':<15}")
        lines.append("-" * 72 + "\n")

        output = "\n".join(lines)

        if to_file:
            with open(to_file, 'w', encoding='utf-8') as f:
                f.write(output)
            save_layout_as_png(output, filename=to_file.replace(".txt", ".png"))
        else:
            print(output)

        print()
        print(centered("=== Mall Layout ===", center_width))
        for floor in self.floors:
            print("\n" + centered(f"--- Floor {floor.f_number + 1} ---", center_width))
            floor.print_floor_layout()
        
        # Legend/Key
        print("\n" + "-" * 72)
        print("Key".center(72))
        print(f"{'[ A ]':<10} {'Agent Start':<15} {'[ ↕ ]':<10} {'Elevator':<15}")
        print(f"{'[ ↑ ]':<10} {'Stairs Up':<15} {'[ ↓ ]':<10} {'Stairs Down':<15}")
        print(f"{'[ S ]':<10} {'Store':<15} {'[ G ]':<10} {'Goal Store':<15}")
        print(f"{'[■■■]':<10} {'Obstacle':<15} {'[   ]':<10} {'Traversal Space':<15}")
        print("-" * 72 + "\n")

def centered(text, width):
    return text.center(width)

### FOR TESTING PURPOSES ONLY ###
if __name__ == "__main__":
    # Create a mall with either store count or density (can mix or swap)
    mall = Mall(
        num_floors=4,
        rows=20,
        columns=20,
        num_elevators= 4
    )

    mall.run_mall_setup()
    mall.print_mall_layout()
    mall.print_mall_layout(to_file="mall_layout.txt")