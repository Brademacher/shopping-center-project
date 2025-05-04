from collections import deque
from interfaces.nodes import Node
from nodecomponents.elevators import Elevator
from nodecomponents.stairs    import Stairs

OPP_DIR = {
    "up": "down", "down": "up",
    "left": "right", "right": "left",
    "up_stairs": "down_stairs", "down_stairs": "up_stairs"
}

def connect_nodes(grid, rows, columns):
    for i in range(rows):
        for j in range(columns):
            node = grid[i][j]
            node.neighbors.clear()

            if node.node_type == "obstacle":
                continue

            if i == 0 and grid[i + 1][j].node_type != "obstacle":
                node.add_neighbor("down", grid[i + 1][j])
            elif i == rows - 1 and grid[i - 1][j].node_type != "obstacle":
                node.add_neighbor("up", grid[i - 1][j])
            elif j == 0 and grid[i][j + 1].node_type != "obstacle":
                node.add_neighbor("right", grid[i][j + 1])
            elif j == columns - 1 and grid[i][j - 1].node_type != "obstacle":
                node.add_neighbor("left", grid[i][j - 1])
            else:
                if grid[i - 1][j].node_type != "obstacle":
                    node.add_neighbor("up", grid[i - 1][j])
                if grid[i + 1][j].node_type != "obstacle":
                    node.add_neighbor("down", grid[i + 1][j])
                if grid[i][j - 1].node_type != "obstacle":
                    node.add_neighbor("left", grid[i][j - 1])
                if grid[i][j + 1].node_type != "obstacle":
                    node.add_neighbor("right", grid[i][j + 1])


def add_inward_neighbor(grid, node, rows, columns):
    inward_dir = get_inward_direction(node.row, node.column, rows, columns)
    if not inward_dir:
        return

    i, j = node.row, node.column
    neighbor = (
        grid[i + 1][j] if inward_dir == "down" else
        grid[i - 1][j] if inward_dir == "up" else
        grid[i][j + 1] if inward_dir == "right" else
        grid[i][j - 1]
    )
    node.add_neighbor(inward_dir, neighbor)

def is_fully_connected(start_node, store_nodes, grid):
    visited = set()
    queue = deque([start_node])
    visited.add((start_node.row, start_node.column, start_node.f_number))

    while queue:
        current = queue.popleft()

        for neighbor_link in current.get_neighbors():
            neighbor = neighbor_link.node
            key = (neighbor.row, neighbor.column, neighbor.f_number)
            if key not in visited and neighbor.node_type != "obstacle":
                visited.add(key)
                queue.append(neighbor)

    # Final check: make sure each store's key is in visited
    for store in store_nodes:
        key = (store.row, store.column, store.f_number)
        if key not in visited:
            return False

    return True

def is_fully_connected_3d(start_node, store_nodes):
    """
    Return True if every node in store_nodes is reachable from start_node
    via ANY neighbor links (horizontal, elevator, or stairs).
    """
    visited = set()
    queue   = deque([start_node])
    visited.add(start_node)

    while queue:
        current = queue.popleft()
        for link in current.get_neighbors():
            nbr = link.node
            if nbr not in visited and nbr.node_type != "obstacle":
                visited.add(nbr)
                queue.append(nbr)

    return all(store in visited for store in store_nodes)


def is_blocking_entry(node, grid, inward_direction_func):
    inward_dir = inward_direction_func(node.row, node.column)
    if not inward_dir:
        return False

    dr, dc = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }[inward_dir]

    r, c = node.row + dr, node.column + dc
    try:
        neighbor = grid[r][c]
        return neighbor.node_type in {"store", "start", "elevator", "stairs"}
    except IndexError:
        return False

def get_inward_direction(row, col, rows, columns):
    if row == 0:
        return "down"
    elif row == rows - 1:
        return "up"
    elif col == 0:
        return "right"
    elif col == columns - 1:
        return "left"
    return None


def is_corner(row, col, rows, columns):
    return (
        (row == 0 and col == 0) or
        (row == 0 and col == columns - 1) or
        (row == rows - 1 and col == 0) or
        (row == rows - 1 and col == columns - 1)
    )

def lock_stair_neighbors(stair_node: Node, allowed_dirs: set[str]) -> None:
    """
    Prune away any neighbor link on stair_node whose direction
    isn't in allowed_dirs. Also remove the corresponding back‐link.
    """
    # work off a copy so we can mutate the real list
    for link in stair_node.get_neighbors()[:]:
        direction = link.direction
        if direction not in allowed_dirs:
            nbr = link.node
            stair_node.remove_neighbor(direction)
            nbr.remove_neighbor(OPP_DIR[direction])

def add_elevator_vertical_neighbors(floors: list):
    """ Connecting up_floor and down_floor elevator neighbors """
    for index, floor in enumerate(floors):
        for elevator in floor.elevators:
            row, column = elevator.row, elevator.column

            # Add up_floor neighbor
            if index < len(floors) -1:
                above = floors[index + 1].grid[row][column]
                if isinstance(above, Elevator):
                    elevator.add_neighbor("up_floor", above, weight = 1.5)
                    above.add_neighbor("down_floor", elevator, weight = 1.5)

            # Add down_floor neighbor
            if index > 0:
                below = floors[index - 1].grid[row][column]
                if isinstance(below, Elevator):
                    elevator.add_neighbor("down_floor", below, weight = 1.5)
                    below.add_neighbor("up_floor", elevator, weight = 1.5)

def update_stair_neighbors(floors: list):
    """ Add stair neighbors for all floors """
    for floor in range(len(floors) - 1):
        lower = floors[floor]
        upper = floors[floor + 1]
        for low in lower.stairs:
            row, column = low.row, low.column

            # Add up_stairs/down_stairs neighbors
            if (column + 1 < upper.columns
                and isinstance(upper.grid[row][column + 1], Stairs)):
                up = upper.grid[row][column + 1]
                low.add_neighbor("up_stairs", up, weight = 2.5)
                up.add_neighbor("down_stairs", low, weight = 2.5)

    """ Remove invalid stair neighbors for all floors """
    for floor_index, floor in enumerate(floors):
        for stair in floor.stairs:
            directions = {left.direction for left in stair.get_neighbors()}
            if "upstairs" in directions:
                lock_stair_neighbors(stair, {"left", "up_stairs"})

            else:
                lock_stair_neighbors(stair, {"right", "down_stairs"})
