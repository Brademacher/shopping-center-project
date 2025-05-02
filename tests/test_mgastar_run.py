from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store
from algorithms.mgastar import MultiGoalAStarPlanner
from agents.mgastar_agent import MultiGoalAStarAgent

# Build and initialize floor
env = Floor(rows=6, columns=8)
env.place_stores(count=5)
env.place_agent_start()
assign_goal_item_to_store(env.stores)

# Set up agent and planner
planner = MultiGoalAStarPlanner()
agent = MultiGoalAStarAgent(planner)

# Run planner
start_node = env.start_node
goal_nodes = env.stores
result = agent.run(env, start_node, goal_nodes)

# Post-run visualization
final_node = None
path = []
expanded = 0
if result:
    path, expanded = result
    final_node = path[-1]

# Identify goal store
goal_store = next((s for s in goal_nodes if s.has_goal_item), None)

# Draw floor layout
print("\nFloor Layout with Agent Path:\n")
path_set = set(path) if path else set()
for row in env.grid:
    row_str = ""
    for node in row:
        if node in path_set:
            row_str += "[ * ]"
        elif node.node_type == "start":
            row_str += "[ A ]"
        elif node.node_type == "store":
            row_str += "[ G ]" if node.has_goal_item else "[ s ]"
        elif node.node_type == "generic":
            row_str += "[   ]"
        else:
            row_str += "[ ? ]"
    print(row_str)

print("\nMulti-Goal A* Agent Results:")
print(f"Nodes expanded: {expanded}")
print(f"Path length: {len(path)}")
print("Path:", [(n.row, n.column) for n in path])
print("Final path ends at:", (final_node.row, final_node.column) if final_node else "None")
print("Goal store is at:", (goal_store.row, goal_store.column) if goal_store else "None")