from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store
from algorithms.dstarlite import DStarLitePlanner
from agents.dstarlite_agent import DStarLiteAgent

# Create floor and set up stores
floor = Floor(rows=6, columns=8)
floor.place_stores(count=5)
floor.place_agent_start()
assign_goal_item_to_store(floor.stores)

# Get start and goal nodes
start_node = floor.start_node
goal_node = next((store for store in floor.stores if store.has_goal_item), None)

if goal_node is None:
    raise ValueError("No goal store assigned!")

# Create agent and planner
planner = DStarLitePlanner()
agent = DStarLiteAgent(planner)
result = agent.run(floor, start_node, [goal_node])

# Visualize result
path = result[0] if result else []
path_set = set(path)
print("\nFloor Layout with D* Lite Path:\n")
for row in floor.grid:
    row_str = ""
    for node in row:
        if node in path_set:
            row_str += "[ * ]"
        elif node == start_node:
            row_str += "[ A ]"
        elif node == goal_node:
            row_str += "[ G ]"
        elif node.node_type == "store":
            row_str += "[ s ]"
        else:
            row_str += "[   ]"
    print(row_str)

print("\nD* Lite Agent Results:")
print(f"Path length: {len(path)}")
print("Path:", [(n.row, n.column) for n in path])
