import csv
import random
import time

from mallcomponents.mall                 import Mall
from agents.astar_agent                  import AStarAgent
from agents.mgastar_agent                import MultiGoalAStarAgent
from agents.dstarlite_agent              import DStarLiteAgent



def compute_path_cost(path):
    cost = 0.0
    for a, b in zip(path, path[1:]):
        for link in a.get_neighbors():
            if link.node is b:
                cost += link.weight
                break
    return cost


def make_mall(seed, **kwargs):
    random.seed(seed)
    m = Mall(
        num_floors=kwargs.get("num_floors", 3),
        rows=kwargs.get("rows", 20),
        columns=kwargs.get("columns", 20),
        stores_per_floor=kwargs.get("stores_per_floor", 5),
        obstacle_density=kwargs.get("obstacle_density", 0.2),
        num_elevators=kwargs.get("num_elevators", 2),
        num_stairs=kwargs.get("num_stairs", 2)
    )
    m.run_mall_setup()
    return m


def run_agent(mall, agent):
    start = mall.floors[mall.agent_start_floor].start_node
    goals = mall.get_all_stores()

    if isinstance(agent, AStarAgent):
        algorithm = "A*"
    elif isinstance(agent, MultiGoalAStarAgent):
        algorithm = "MultiGoal-A*"
    elif isinstance(agent, DStarLiteAgent):
        algorithm = "D* Lite"
    else:
        raise ValueError("Unknown agent type") 

    t0 = time.perf_counter()
    path, expanded, length, cost = agent.run(
        env=mall,
        start_node=start,
        goal_nodes=goals
    )
    compute_time = time.perf_counter() - t0

    return {
        "algorithm":   algorithm,
        "expanded":    expanded,
        "time":        compute_time,
        "path_length": length,
        "path_cost":   cost,
        "ends_at":     (path[-1].row, path[-1].column, path[-1].f_number)
                       if path else None
    }

def main():
    SEEDS   = list(range(10))
    CONFIGS = [
        {"num_floors": 3, "rows": 20, "columns": 20, "stores_per_floor": 10, "obstacle_density": 0.2, "num_elevators": 5, "num_stairs": 5},
    ]
    agents_list = [
        AStarAgent(),
        MultiGoalAStarAgent(),
        DStarLiteAgent()
    ]
    all_results = []
    for cfg in CONFIGS:
        for seed in SEEDS:
            mall = make_mall(seed, **cfg)
            for agent in agents_list:
                res = run_agent(mall, agent)
                res.update({
                    "seed":      seed,
                    "elevators": cfg["num_elevators"],
                    "stairs":    cfg["num_stairs"],
                })
                all_results.append(res)

    # Compute and print averages
    summary = {}
    for r in all_results:
        key = (r["algorithm"], r["elevators"], r["stairs"])
        stats = summary.setdefault(key, {
            "count":    0,
            "sum_len":  0,
            "sum_cost": 0.0,
            "sum_exp":  0,
            "sum_time": 0.0,   
        })
        stats["count"]   += 1
        stats["sum_len"] += r["path_length"]
        stats["sum_cost"]+= r["path_cost"]
        stats["sum_exp"] += r["expanded"]
        stats["sum_time"]+= r["time"]         

    # Print summary
    sim_cnt = stats["count"]
    f_count = len(mall.floors)
    rows    = mall.rows
    cols    = mall.columns
    m_count = len(mall.get_all_stores())
    o_count  = sum(mall.get_obstacle_placement_count(f) for f in mall.floors)

    print("\n" + "--- Setup ---".center(90))
    print(f"{'Total Simulations':<19} {'Floors':<8} {'Rows':<6} {'Columns':<9} {'Stores Per Floor':<18} {'Obstacles':<11} {'Elevators':<11} {'Stairs':<8}")
    print(f"{sim_cnt:>17} {f_count:>8} {rows:>6} {cols:>9} {m_count:>18} {o_count:>11} {cfg['num_elevators']:>11} {cfg['num_stairs']:>8}")

    print("\n" + "--- Averages ---".center(75))
    print(f"{'Alg':<15} {'Avg Path Length':>17} {'Avg Cost':>10} {'Avg Expansions':>16} {'Avg Comp Time(s)':>17}")
    for (alg, e, s), stats in summary.items():
        cnt = stats["count"]
        avg_len  = stats["sum_len"]  / cnt
        avg_cost = stats["sum_cost"] / cnt
        avg_exp  = stats["sum_exp"]  / cnt
        avg_time = stats["sum_time"] / cnt    
        print(f"{alg:<16}"
              f"{avg_len:17.2f} {avg_cost:10.2f} {avg_exp:16.2f} {avg_time:17.4f}")

    # Write CSV
    fieldnames = [
        "seed", "elevators", "stairs",
        "algorithm", "expanded", "path_length", "path_cost", "ends_at","time"
    ]
    with open("batch_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print("\nWrote batch_results.csv")


if __name__ == "__main__":
    main()
