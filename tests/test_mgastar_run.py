import time
from agents.mgastar_agent import MultiGoalAStarAgent
from algorithms.mgastar import MultiGoalAStarPlanner
from mallcomponents.floor import Floor
from nodecomponents.goal_logic import assign_goal_item_to_store

# --- Wrap MultiGoalAStarPlanner.plan() to record compute time and capture sorted_goals ---
real_planner = MultiGoalAStarPlanner()
compute_times = []
plan_outputs = []  # will store the sorted_goals list
orig_plan = real_planner.plan

def timed_plan(env, start, goals):
    t0 = time.perf_counter()
    sorted_goals, expanded = orig_plan(env, start, goals)
    compute_times.append(time.perf_counter() - t0)
    plan_outputs.append(sorted_goals)
    return sorted_goals, expanded

real_planner.plan = timed_plan
agent = MultiGoalAStarAgent(planner=real_planner)

# --- Environment Setup ---
floor = Floor(rows=100, columns=100, f_number=0)
floor.place_agent_start()
floor.place_stores(count=500)
assign_goal_item_to_store(floor.stores)
floor.place_obstacles(count=6600)

def main():
    # 1 Measure total wall-clock runtime
    t_start = time.perf_counter()
    result = agent.run(
        env=floor,
        start_node=floor.start_node,
        goal_nodes=floor.stores
    )
    total_time = time.perf_counter()

    result = agent.run(
        env=floor,
        start_node=floor.start_node,
        goal_nodes=floor.stores
    )

    compute_time = sum(compute_times)

    # Determine replans as segments - 1
    if plan_outputs:
        segments = len(plan_outputs[0])
        replans = max(0, segments - 1)
    else:
        replans = 0

    # Calculate replans
    sorted_goals = plan_outputs[0]
    goal_index = next(
        i for i, seg in enumerate(sorted_goals)
        if seg["goal"].has_goal_item
    )
    replans = goal_index
    total_cost = sum(seg["cost"] for seg in sorted_goals[:goal_index + 1])

    # Unpack results
    if result:
        path_taken, expanded, goal_store = result
    else:
        path_taken, expanded, goal_store = [], 0, None

    # 2 Display the floor and the results
    if path_taken:
        print(" ")
    else:
        print("No path was found to any store.")

    total_time = time.perf_counter() - t_start

    print("\nMulti-Goal A* Metrics Summary:")
    print(f"total_time:    {(total_time * 100):.5f}")
    print(f"compute_time:  {(compute_time * 100):.5f}")
    print(f"replans:       {replans}")
    print(f"steps_taken:   {agent.total_steps}")
    print(f"nodes_expanded:{agent.total_expansions}")


    # Compute total path cost
    cost = 0
    for i in range(len(path_taken) - 1):
        cur, nxt = path_taken[i], path_taken[i+1]
        for link in cur.get_neighbors():
            if link.node == nxt:
                cost += link.weight
                break

    print(f"path_cost:     {total_cost}")
    print(f"success:       {agent.success}")

    if goal_store:
        print(f"Final path ends at: ({path_taken[-1].row},{path_taken[-1].column})")
        print(f"Goal store is at:   ({goal_store.row},{goal_store.column})")

if __name__ == "__main__":
    main()
