# tests/test_mgastar_run.py

from mallcomponents.mall                import Mall
from nodecomponents.goal_logic          import assign_goal_item_to_store
from agents.mgastar_agent               import MultiGoalAStarAgent
from algorithms.mgastar                 import MultiGoalAStarPlanner

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

    # 2) build everything (agent, stores, obstacles, elevators, stairs, goal item)
    mall.run_mall_setup()

    # 3) collect start & goals across all floors
    start_node = mall.floors[mall.agent_start_floor].start_node
    goal_nodes = mall.get_all_stores()

    # 4) run multi-goal A*
    agent   = MultiGoalAStarAgent(planner=MultiGoalAStarPlanner())
    path, expanded = agent.run(
        env=mall,
        start_node=start_node,
        goal_nodes=goal_nodes
    )

    # 5) print per-floor layout with agent path
    for floor in mall.floors:
        nodes_on = [n for n in path if n.f_number == floor.f_number]
        print(f"\n--- Floor {floor.f_number} ---")
        floor.print_floor_layout_with_obstacles(path_nodes=nodes_on)

    # 6) summary
    print("\nMulti-Goal A* Agent Results:")
    print(f"  Nodes expanded: {expanded}")
    print(f"  Path length:    {len(path)}")
    print("  Full path (row,col,floor):")
    print("   ", [(n.row, n.column, n.f_number) for n in path])
    if path:
        end = path[-1]
        print(f"  Final path ends at: ({end.row},{end.column}, floor {end.f_number})")
        goal = next(s for s in goal_nodes if s.has_goal_item)
        print(f"  Goal store is at:   ({goal.row},{goal.column}, floor {goal.f_number})")
    else:
        print("✘ No path was found to any store.")

if __name__ == "__main__":
    main()
