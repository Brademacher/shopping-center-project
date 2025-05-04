from mallcomponents.mall          import Mall
from agents.astar_agent           import AStarAgent
from algorithms.astar             import AStarPlanner

def main():
    # 1) configure a 3D mall (3 floors, 10×12 each)
    mall = Mall(
        num_floors=3,
        rows=10,
        columns=12,
        stores_per_floor=6,        # or use store_density
        obstacles_per_floor=10,    # or obstacle_density
        num_elevators=2,           # elevator shafts
        num_stairs=2,              # stair flights
    )

    # 2) build everything: agent, stores, obstacles, elevators, stairs, goal items
    mall.run_mall_setup()

    # 3) pick the start node where the agent is placed
    start_node = mall.floors[mall.agent_start_floor].start_node

    # 4) gather every store in the mall as a possible goal
    goal_nodes = mall.get_all_stores()

    # 5) run your existing A* agent code
    agent = AStarAgent(planner=AStarPlanner())
    path, expanded = agent.run(
        env=mall,           # your agent only really cares about start_node & neighbors
        start_node=start_node,
        goal_nodes=goal_nodes
    )

    # 6) print a per‐floor view of the found path
    for floor in mall.floors:
        # filter path nodes down to this floor
        nodes_on_floor = [n for n in path if n.f_number == floor.f_number]

        print(f"\n--- Floor {floor.f_number} ---")
        floor.print_floor_layout_with_obstacles(path_nodes=nodes_on_floor)

    # 7) final summary
    print("\nA* Agent Results:")
    print(f"  Nodes expanded: {expanded}")
    print(f"  Path length:    {len(path)}")
    print("  Full path by (row,column,floor):")
    print("   ", [(n.row,n.column,n.f_number) for n in path])
    if path:
        end = path[-1]
        print(f"  Final path ends at: ({end.row},{end.column}, floor {end.f_number})")
    goal = next(s for s in goal_nodes if s.has_goal_item)
    print(f"  Goal store is at:   ({goal.row},{goal.column}, floor {goal.f_number})")

if __name__ == "__main__":
    main()