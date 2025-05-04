# run_simulations.py

import csv
import random

from mallcomponents.mall                import Mall
from agents.astar_agent                  import AStarAgent
from algorithms.astar                    import AStarPlanner
from agents.mgastar_agent                import MultiGoalAStarAgent
from algorithms.mgastar                  import MultiGoalAStarPlanner
from agents.dstarlite_agent              import DStarLiteAgent
from algorithms.dstarlite                import DStarLitePlanner


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
        num_floors=5,
        rows=45,
        columns=45,
        stores_per_floor=13,
        num_elevators=kwargs.get("num_elevators", 2),
        num_stairs=kwargs.get("num_stairs", 2),
    )
    m.run_mall_setup()
    return m


def run_astar(mall):
    start = mall.floors[mall.agent_start_floor].start_node
    # we now pass *all* stores into the agent; it will sort & pick the one with the item
    path, expanded, total_length, total_cost = AStarAgent().run(
        env=mall,
        start_node=start,
        goal_nodes=mall.get_all_stores()
    )

    return {
        "algorithm":   "A*",
        "expanded":    expanded,
        "path_length": total_length,
        "path_cost":   total_cost,
        "ends_at":     (path[-1].row, path[-1].column, path[-1].f_number)
                     if path else None
    }


def run_mgastar(mall):
    start = mall.floors[mall.agent_start_floor].start_node
    goals = mall.get_all_stores()

    path, expanded, length, cost = MultiGoalAStarAgent(
        MultiGoalAStarPlanner()
    ).run(env=mall, start_node=start, goal_nodes=goals)

    return {
        "algorithm":   "MultiGoal-A*",
        "expanded":    expanded,
        "path_length": length,
        "path_cost":   cost,
        "ends_at":     (path[-1].row, path[-1].column, path[-1].f_number)
                      if path else None
    }

def run_dstarlite(mall):
    start = mall.floors[mall.agent_start_floor].start_node
    goal  = next(s for s in mall.get_all_stores() if s.has_goal_item)

    # ← unpack four values, not three
    path, expanded, length, cost = DStarLiteAgent(
        DStarLitePlanner()
    ).run(env=mall, start_node=start, goal_nodes=[goal])

    return {
        "algorithm":   "D* Lite",
        "expanded":    expanded,
        "path_length": length,   # use the returned length
        "path_cost":   cost,     # use the returned cost
        "ends_at":     (path[-1].row, path[-1].column, path[-1].f_number)
                       if path else None
    }


def main():
    SEEDS   = list(range(10))
    CONFIGS = [
        {"num_elevators": 5, "num_stairs": 5},
        {"num_elevators": 3, "num_stairs": 3},
    ]

    all_results = []
    for cfg in CONFIGS:
        for seed in SEEDS:
            mall = make_mall(seed, **cfg)
            for fn in (run_astar, run_mgastar, run_dstarlite):
                res = fn(mall)
                res.update({
                    "seed":      seed,
                    "elevators": cfg["num_elevators"],
                    "stairs":    cfg["num_stairs"],
                })
                all_results.append(res)

    # 1) Print per-trial results
    print(f"{'Alg':<15} {'E':>2} {'S':>2} {'Seed':>4} "
          f"{'Len':>5} {'Cost':>7} {'Exp':>7} {'End (r,c,f)':>20}")
    for r in all_results:
        ends = str(r["ends_at"]) if r["ends_at"] else "<none>"
        print(f"{r['algorithm']:<15} {r['elevators']:>2} {r['stairs']:>2} "
              f"{r['seed']:>4} {r['path_length']:>5} {r['path_cost']:>7.2f} "
              f"{r['expanded']:>7} {ends:>20}")

    # 2) Compute and print averages
    summary = {}
    for r in all_results:
        key = (r["algorithm"], r["elevators"], r["stairs"])
        stats = summary.setdefault(key, {"count":0, "sum_len":0, "sum_cost":0.0, "sum_exp":0})
        stats["count"]   += 1
        stats["sum_len"] += r["path_length"]
        stats["sum_cost"]+= r["path_cost"]
        stats["sum_exp"] += r["expanded"]

    print("\n--- Averages ---")
    print(f"{'Alg':<15} {'E':>2} {'S':>2} {'AvgLen':>7} {'AvgCost':>8} {'AvgExp':>8}")
    for (alg, e, s), stats in summary.items():
        cnt = stats["count"]
        avg_len  = stats["sum_len"] / cnt
        avg_cost = stats["sum_cost"]/ cnt
        avg_exp  = stats["sum_exp"] / cnt
        print(f"{alg:<15} {e:>2} {s:>2} {avg_len:7.2f} {avg_cost:8.2f} {avg_exp:8.2f}")

    # 3) Write CSV
    fieldnames = [
        "seed", "elevators", "stairs",
        "algorithm", "expanded", "path_length", "path_cost", "ends_at"
    ]
    with open("batch_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    print("\nWrote batch_results.csv")


if __name__ == "__main__":
    main()
