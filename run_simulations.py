import csv
from mallcomponents.mall                import Mall
from agents.astar_agent                  import AStarAgent
from algorithms.astar                    import AStarPlanner
from agents.mgastar_agent                import MultiGoalAStarAgent
from algorithms.mgastar                  import MultiGoalAStarPlanner
from agents.dstarlite_agent              import DStarLiteAgent
from algorithms.dstarlite                import DStarLitePlanner

def make_mall(seed=None):
    m = Mall(
        num_floors=3,
        rows=20,
        columns=20,
        stores_per_floor=8,
        num_elevators=3,
        num_stairs=3,
    )
    if seed is not None:
        import random
        random.seed(seed)
    m.run_mall_setup()
    return m

def run_astar(mall):
    agent = AStarAgent(planner=AStarPlanner())
    start = mall.floors[mall.agent_start_floor].start_node
    goals = mall.get_all_stores()
    path, expanded = agent.run(env=mall, start_node=start, goal_nodes=goals)
    return {
        "name":"A*", 
        "expanded": expanded, 
        "path_length": len(path),
        "ends_at": (path[-1].row, path[-1].column, path[-1].f_number)
    }

def run_mgastar(mall):
    agent = MultiGoalAStarAgent(planner=MultiGoalAStarPlanner())
    start = mall.floors[mall.agent_start_floor].start_node
    goals = mall.get_all_stores()
    path, expanded, reached = agent.run(env=mall, start_node=start, goal_nodes=goals)
    return {
        "name":"MultiGoal-A*", 
        "expanded": expanded, 
        "path_length": len(path),
        "ends_at": (path[-1].row, path[-1].column, path[-1].f_number)
    }

def run_dstarlite(mall):
    agent = DStarLiteAgent(planner=DStarLitePlanner())
    start = mall.floors[mall.agent_start_floor].start_node
    goal = [s for s in mall.get_all_stores() if s.has_goal_item][0]
    path, expanded = agent.run(env=mall, start_node=start, goal_nodes=[goal])
    return {
        "name":"D* Lite", 
        "expanded": expanded, 
        "path_length": len(path),
        "ends_at": (path[-1].row, path[-1].column, path[-1].f_number)
    }

def main():
    # Single environment, same for all three
    mall = make_mall(seed=42)

    results = []
    for fn in (run_astar, run_mgastar, run_dstarlite):
        res = fn(mall)
        results.append(res)

    # Print results in a table
    print(f"{'Alg':<15} {'Expanded':>8} {'PathLen':>8} {'End (r,c,f)':>20}")
    for r in results:
        print(f"{r['name']:<15} {r['expanded']:>8} {r['path_length']:>8} {str(r['ends_at']):>20}")

    # Optionally: write CSV
    with open("simulation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name","expanded","path_length","ends_at"])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print("\nWrote simulation_results.csv")

if __name__ == "__main__":
    main()