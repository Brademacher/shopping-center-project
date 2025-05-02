# tests/test_mgastar_run.py
from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store
from agents.mgastar_agent import MultiGoalAStarAgent
from algorithms.mgastar import MultiGoalAStarPlanner

floor = Floor(rows=10, columns=12, f_number=0)
floor.place_agent_start()
floor.place_stores(count=6)
assign_goal_item_to_store(floor.stores)
placed = floor.place_obstacles(count=10)
print(f"Placed {placed} out of 10 obstacles.")

agent = MultiGoalAStarAgent(planner=MultiGoalAStarPlanner())
result = agent.run(env=floor, start_node=floor.start_node, goal_nodes=floor.stores)

if result:
    path, expanded = result
    goal = path[-1] if path else None  # approximate
    floor.print_floor_layout_with_obstacles(path_nodes=path)

    print("\nMulti-Goal A* Agent Results:")
    print(f"Nodes expanded: {expanded}")
    print(f"Path length: {len(path)}")
    print(f"Path: {[ (n.row, n.column) for n in path ]}")
    if path:
        print(f"Final path ends at: ({path[-1].row},{path[-1].column})")
    else:
        print("No path was found to any store.")
    print(f"Goal store is at:   ({goal.row},{goal.column})")
else:
    floor.print_floor_layout_with_obstacles()  # show grid even if no path
    print("✘ No goal store could be reached.")