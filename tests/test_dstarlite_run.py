import time
from agents.dstarlite_agent import DStarLiteAgent
from algorithms.dstarlite import DStarLitePlanner
from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store

# --- Wrap DStarLitePlanner.plan() to record each call’s compute time ---
real_planner  = DStarLitePlanner()
compute_times = []
_orig_plan    = real_planner.plan

def timed_plan(env, start_node, goal_node):
    t0 = time.perf_counter()
    result = _orig_plan(env, start_node, goal_node)
    compute_times.append(time.perf_counter() - t0)
    return result

real_planner.plan = timed_plan
agent = DStarLiteAgent(real_planner)

# --- Environment Setup ---
floor = Floor(rows=100, columns=100, f_number=0)
floor.place_agent_start()
floor.place_stores(count=500)
assign_goal_item_to_store(floor.stores)
floor.place_obstacles(count=6600)

# --- Locate the goal store ---
goal_store = next(store for store in floor.stores if store.has_goal_item)

def main():
    # 1) Measure total wall-clock runtime
    t_start = time.perf_counter()
    path, expanded = agent.run(
        floor,
        start_node=floor.start_node,
        goal_nodes=floor.stores
    )
    total_time   = time.perf_counter() - t_start
    compute_time = sum(compute_times)

    # 2) Display the floor and the results
    floor.print_floor_layout_with_obstacles(path_nodes=path if path else [])

    print("\nD* Lite Results:")
    print(f"total_time:    {total_time}")
    print(f"compute_time:  {compute_time}")
    print(f"replans:       {agent.total_replans}")
    print(f"steps_taken:   {agent.total_steps}")
    print(f"nodes_expanded:{agent.total_expansions}")
    print(f"path_cost:     {agent.total_path_cost}")
    print(f"success:       {agent.success}")
    if path:
        print(f"Final path ends at: ({path[-1].row},{path[-1].column})")
        print(f"Goal store is at:   ({goal_store.row},{goal_store.column})")
    else:
        print("✘ No path found.")

if __name__ == "__main__":
    main()
