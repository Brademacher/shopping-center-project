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
        {"num_floors": 4, "rows": 55, "columns": 55, "stores_per_floor": 20, "obstacle_density": 0.40, "num_elevators": 6, "num_stairs": 6}
    ]
    agents_list = [
        AStarAgent(),
        MultiGoalAStarAgent(),
        DStarLiteAgent()
    ]
    all_results = []

    # --- Run all simulations ---
    for cfg in CONFIGS:
        for seed in SEEDS:
            mall = make_mall(seed, **cfg)
            for agent in agents_list:
                res = run_agent(mall, agent)
                res.update({
                    "seed": seed,
                    "elevators": cfg["num_elevators"],
                    "stairs": cfg["num_stairs"],
                    "rows": cfg["rows"],
                    "columns": cfg["columns"],
                    "num_floors": cfg["num_floors"],
                    "stores_per_floor": cfg["stores_per_floor"],
                    "obstacle_density": cfg["obstacle_density"]
                })
                all_results.append(res)

    # --- Compute summaries ---
    summary = {}
    for r in all_results:
        key = (
            r["algorithm"], r["elevators"], r["stairs"],
            r["rows"], r["columns"], r["num_floors"],
            r["stores_per_floor"], r["obstacle_density"]
        )
        stats = summary.setdefault(key, {
            "count": 0,
            "sum_len": 0,
            "sum_cost": 0.0,
            "sum_exp": 0,
            "sum_time": 0.0
        })
        stats["count"] += 1
        stats["sum_len"] += r["path_length"]
        stats["sum_cost"] += r["path_cost"]
        stats["sum_exp"] += r["expanded"]
        stats["sum_time"] += r["time"]

    # --- Print summary grouped by config ---
    printed_configs = set()
    for (alg, e, s, rows, cols, floors, spf, odens), stats in summary.items():
        config_key = (e, s, rows, cols, floors, spf, odens)
        if config_key not in printed_configs:
            printed_configs.add(config_key)
            
            print("\n" + "-" * 72)
            print("--- Setup ---".center(72))
            print(f"{'Floors':<8} {'Rows':<6} {'Cols':<6} {'Stores/Floor':<15} "
                  f"{'Obst. Density':<15} {'Elevators':<10} {'Stairs':<8}")
            print(f"{floors:>6} {rows:>6} {cols:>6} {spf:>14} "
                  f"{odens:>16.2f} {e:>10} {s:>8}")

            print("\n" + "--- Averages ---".center(72))
            print(f"{'Alg':<15} {'Avg Len':>10} {'Avg Cost':>10} "
                  f"{'Avg Exp':>12} {'Avg Time(s)':>14}")

        cnt = stats["count"]
        avg_len = stats["sum_len"] / cnt
        avg_cost = stats["sum_cost"] / cnt
        avg_exp = stats["sum_exp"] / cnt
        avg_time = stats["sum_time"] / cnt

        print(f"{alg:<15} {avg_len:10.2f} {avg_cost:10.2f} "
              f"{avg_exp:12.2f} {avg_time:14.4f}")
    print("-" * 72 + "\n") 

    # --- Save to CSV ---
    with open("batch_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "seed", "elevators", "stairs", "rows", "columns",
            "num_floors", "stores_per_floor", "obstacle_density",
            "algorithm", "expanded", "path_length", "path_cost", "ends_at", "time"
        ])
        writer.writeheader()
        writer.writerows(all_results)

    print("\nWrote batch_results.csv")


if __name__ == "__main__":
    main()
