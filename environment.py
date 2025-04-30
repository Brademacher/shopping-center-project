import random
import json

# Building 3D environment for agent testing #
class MallEnvironment:
    def __init__(self, length, width, floor, num_stores=0, num_obstacles=0, num_elevators=0, num_escalators=0):
        self.length = length
        self.width = width
        self.floor = floor
        self.num_stores = num_stores
        self.num_obstacles = num_obstacles
        self.num_elevators = num_elevators
        self.num_escalators = num_escalators
        self.start = (0, 0, 0)

        self.grid = self.__create__empty__grid()
        self.elevators = {}
        self.escalators = {}
        self.stores = []
        self.visited_stores = []
        self.goal_store_trigger_index = None
        self.goal_reached = False
        self.obstacles = {}

        self.grid[self.start[2]][self.start[1]][self.start[0]] = 0  # ensure start is clear

        self.__place_obstacles()
        self.__place_elevators()
        self.__place_escalators()
        self.__place_stores()

    def __create__empty__grid(self):
        return [[[0 for _ in range(self.length)] for _ in range(self.width)] for _ in range(self.floor)]

    def __place_obstacles(self):
        placed = 0
        while placed < self.num_obstacles:
            f = random.randint(0, self.floor - 1)
            x = random.randint(1, self.length - 2)
            y = random.randint(1, self.width - 2)
            if (x, y, f) != self.start and self.grid[f][y][x] == 0:
                self.grid[f][y][x] = "X"
                self.obstacles[(x, y, f)] = True
                placed += 1

    def __place_elevators(self):
        placed = 0
        while placed < self.num_elevators:
            x = random.randint(0, self.length - 1)
            y = random.randint(0, self.width - 1)
            if (x, y) != self.start[:2] and all(self.grid[f][y][x] == 0 for f in range(self.floor)):
                label = f"E{placed + 1}"
                for f in range(self.floor):
                    self.grid[f][y][x] = label
                self.elevators[label] = {"coords": (x, y), "floors": list(range(self.floor))}
                placed += 1

    def __place_escalators(self):
        placed = 0
        while placed < self.num_escalators:
            f = random.randint(0, self.floor - 2)
            x = random.randint(0, self.length - 1)
            y = random.randint(1, self.width - 2)
            dy = random.choice([-1, 1])
            y_upper = y + dy
            if (x, y, f) != self.start and self.grid[f][y][x] == 0 and self.grid[f + 1][y_upper][x] == 0:
                label = f"ES{placed + 1}"
                self.grid[f][y][x] = label + "↑"
                self.grid[f + 1][y_upper][x] = label + "↓"
                self.escalators[label] = {
                    "lower_coords": (x, y, f),
                    "upper_coords": (x, y_upper, f + 1),
                    "from_to": (f, f + 1)
                }
                placed += 1

    def __place_stores(self):
        placed = 0
        while placed < self.num_stores:
            f = random.randint(0, self.floor - 1)
            side = random.choice(["top", "bottom", "left", "right"])
            if side in ["top", "bottom"]:
                y = 0 if side == "top" else self.width - 1
                x = random.randint(0, self.length - 1)
            else:
                x = 0 if side == "left" else self.length - 1
                y = random.randint(0, self.width - 1)
            if (
                self.grid[f][y][x] == 0 and
                (x, y, f) != self.start and
                all((x, y, f) != coords for coords in self.obstacles) and
                all((x, y) != e["coords"] for e in self.elevators.values()) and
                all((x, y, f) != e["lower_coords"] and (x, y, f) != e["upper_coords"] for e in self.escalators.values())
            ):
                self.grid[f][y][x] = "S"
                self.stores.append((x, y, f))
                placed += 1

    def set_goal_trigger_index(self, index):
        if not (0 <= index < self.num_stores):
            print("Invalid store goal index")
            return
        self.goal_store_trigger_index = index

    def visit_store(self, x, y, f):
        if not (0 <= f < self.floor and 0 <= y < self.width and 0 <= x < self.length):
            return
        if (x, y, f) in self.stores and (x, y, f) not in self.visited_stores:
            self.visited_stores.append((x, y, f))
        if self.goal_store_trigger_index is not None and len(self.visited_stores) > self.goal_store_trigger_index:
            self.goal_reached = True

    def get_neighbors(self, x, y, f):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.length and 0 <= ny < self.width:
                if self.grid[f][ny][nx] != "X":
                    neighbors.append((nx, ny, f, 1))

        for label, data in self.elevators.items():
            ex, ey = data["coords"]
            if (x, y) == (ex, ey) and f in data["floors"]:
                for floor in data["floors"]:
                    if floor != f and self.grid[floor][y][x] != "X":
                        cost = 1.5 * abs(floor - f)
                        neighbors.append((x, y, floor, cost))

        for label, data in self.escalators.items():
            lx, ly, lf = data["lower_coords"]
            ux, uy, uf = data["upper_coords"]
            if (x, y, f) == (lx, ly, lf):
                if self.grid[uf][uy][ux] != "X":
                    neighbors.append((ux, uy, uf, 2))

        return neighbors

    def print_floor(self, floorIndex):
        if 0 <= floorIndex < self.floor:
            print(f"\nFloor {floorIndex}:")
            for row in self.grid[floorIndex]:
                row_str = " ".join(f"{str(cell):>6}" for cell in row)
                print(row_str)
        else:
            print("Invalid floor index. Please choose a valid floor.")

    def print_all_floors(self):
        for floorIndex in range(self.floor):
            self.print_floor(floorIndex)

    def list_stores(self):
        print("\nStore locations:")
        for i, (x, y, f) in enumerate(self.stores):
            print(f"Store {i}: ({x}, {y}, floor {f})")

    def __str__(self):
        return (
            f"MallEnvironment: {self.length}x{self.width}x{self.floor} floors\n"
            f"  Stores: {self.num_stores}, Obstacles: {self.num_obstacles}, "
            f"Elevators: {self.num_elevators}, Escalators: {self.num_escalators}"
        )

    def to_json(self, path):
        data = {
            "length": self.length,
            "width": self.width,
            "floor": self.floor,
            "grid": self.grid,
            "stores": self.stores,
            "obstacles": list(self.obstacles.keys()),
            "elevators": self.elevators,
            "escalators": self.escalators,
            "goal_store_trigger_index": self.goal_store_trigger_index,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def from_json(cls, path):
        with open(path, 'r') as f:
            data = json.load(f)

        env = cls(length=data["length"], width=data["width"], floor=data["floor"])
        env.grid = data["grid"]
        env.stores = [tuple(s) for s in data["stores"]]
        env.obstacles = {tuple(o): True for o in data["obstacles"]}
        env.elevators = {
            label: {
                "coords": tuple(info["coords"]),
                "floors": info["floors"]
            }
            for label, info in data["elevators"].items()
        }
        env.escalators = {
            label: {
                "lower_coords": tuple(info["lower_coords"]),
                "upper_coords": tuple(info["upper_coords"]),
                "from_to": tuple(info["from_to"])
            }
            for label, info in data["escalators"].items()
        }
        env.goal_store_trigger_index = data["goal_store_trigger_index"]
        return env
