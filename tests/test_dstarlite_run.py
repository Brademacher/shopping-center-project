# tests/test_dstarlite_run.py

from mallcomponents.mall               import Mall
from nodecomponents.goal_logic         import assign_goal_item_to_store
from agents.dstarlite_agent            import DStarLiteAgent
from algorithms.dstarlite               import DStarLitePlanner

def main():
    # 1) configure a 3D mall
    mall = Mall(
        num_floors=3,
        rows=10,
        columns=12,
        stores_per_floor=6,
        obstacles_per_floor=10,
        num_elevators=2,
        num_stairs=2,
    )

    # 2) build everything (agent start, stores, obstacles, elevators, stairs, goal item)
    mall.run_mall_setup()

    # 3) pick start & goal
    start_node = mall.floors[mall.agent_start_floor].start_node
    goal_store = next(s for s in mall.get_all_stores() if s.has_goal_item)

    # 4) show the empty mall
    print(f"Goal store will be at: ({goal_store.row},{goal_store.column}, floor {goal_store.f_number})")
    print("Initial Mall Layout:")
    for floor in mall.floors:
        print(f"\n--- Floor {floor.f_number} ---")
        floor.print_floor_layout()

    # 5) run D* Lite to that single goal
    agent   = DStarLiteAgent(planner=DStarLitePlanner())
    path, expanded = agent.run(
        env=mall,
        start_node=start_node,
        goal_nodes=[goal_store]
    )

    # 6) print the resulting path per floor
    for floor in mall.floors:
        nodes_on = [n for n in path if n.f_number == floor.f_number]
        print(f"\n--- Floor {floor.f_number} (with path) ---")
        floor.print_floor_layout(path_nodes=nodes_on)

    # 7) summary
    print("\nD* Lite Agent Results:")
    print(f"  Nodes expanded (approx): {expanded}")
    print(f"  Path length:            {len(path)}")
    print("  Full path (row,col,floor):")
    print("   ", [(n.row, n.column, n.f_number) for n in path])
    if path:
        end = path[-1]
        print(f"  Final path ends at: ({end.row},{end.column}, floor {end.f_number})")
    else:
        print("✘ No path was found to the goal store.")

if __name__ == "__main__":
    main()
