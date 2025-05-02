# tests/test_dstarlite_run.py
from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store
from agents.dstarlite_agent import DStarLiteAgent
from algorithms.dstarlite import DStarLitePlanner

floor = Floor(rows=10, columns=12, f_number=0)
floor.place_agent_start()
floor.place_stores(count=6)
assign_goal_item_to_store(floor.stores)
floor.place_obstacles(count=10)

goal_store = next(s for s in floor.stores if s.has_goal_item)
agent = DStarLiteAgent(planner=DStarLitePlanner())
result = agent.run(env=floor, start_node=floor.start_node, goal_nodes=[goal_store])

if result:
    path, expanded = result
    floor.print_floor_layout_with_obstacles(path_nodes=path)
    print("\nD* Lite Results:")
    print(f"Nodes expanded (approx): {expanded}")
    print(f"Path length: {len(path)}")
    print(f"Path: {[ (n.row, n.column) for n in path ]}")
    print(f"Final path ends at: ({path[-1].row},{path[-1].column})")
    print(f"Goal store is at:   ({goal_store.row},{goal_store.column})")
else:
    floor.print_floor_layout_with_obstacles()
    print("✘ No path found.")
