from mallcomponents.floor import Floor
from agents.astar_agent import AStarAgent
from algorithms.astar import AStarPlanner
from nodecomponents.goal_logic import assign_goal_item_to_store

# Build and set up the floor
floor = Floor(rows=6, columns=8)
floor.place_stores(count=5)
floor.place_agent_start()
assign_goal_item_to_store(floor.stores)

# Run A* agent
planner = AStarPlanner()
agent = AStarAgent(planner)
start = floor.start_node
path, expanded = agent.run(env=floor, start_node=start, goal_nodes=floor.stores)

# Display floor layout and path
print("\nFloor Layout with Agent Path:\n")

path_set = set(path)  # for fast lookup

for row in floor.grid:
    row_str = ""
    for node in row:
        if node in path_set:
            row_str += "[ * ]"  # node is part of the A* path
        elif node.node_type == "start":
            row_str += "[ A ]"
        elif node.node_type == "store":
            row_str += "[ G ]" if node.has_goal_item else "[ s ]"
        elif node.node_type == "generic":
            row_str += "[   ]"
        else:
            row_str += "[ ? ]"
    print(row_str)

# Display results
print(f"\nA* Agent Results:")
print(f"Nodes expanded: {expanded}")
print(f"Path length: {len(path)}")
print("Path:", [(n.row, n.column) for n in path])
print("Final path ends at:", (path[-1].row, path[-1].column))
print("Goal store is at:  ", (next(s for s in floor.stores if s.has_goal_item).row,
                               next(s for s in floor.stores if s.has_goal_item).column))
