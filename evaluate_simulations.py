"""
Evaluate A*, D*-Lite, and Greedy Multi-Goal A* on every saved simulation.

All planners share the same compulsory “trigger” store, and an episode
finishes only after ≥ 6 distinct stores *and* that trigger store have
been visited.

Outputs
-------
paths/<algo>/<sim_id>.csv   – full coordinate path
results.csv                 – summary metrics
"""

import os
import csv
from tqdm import tqdm
from environment import MallEnvironment

# Planners
from algorithms.astar     import AStarPlanner
from algorithms.dstarlite import DStarLitePlanner
from algorithms.mgastar   import MultiGoalAStarPlanner

# Agents
from agents.astar_agent     import AStarAgent
from agents.dstarlite_agent import DStarLiteAgent
from agents.mgastar_agent   import MultiGoalAStarAgent

# ---------------------------------------------------------------------
# Create output folders
# ---------------------------------------------------------------------
for sub in ("astar", "dstarlite", "mgastar"):
    os.makedirs(f"paths/{sub}", exist_ok=True)

# ---------------------------------------------------------------------
# Helper to drive an agent until done
# ---------------------------------------------------------------------
def run_episode(agent, env):
    path = [env.agent_pos]
    while agent.step():
        path.append(env.agent_pos)
    return path

# ---------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------
with open("results.csv", "w", newline="") as results_file:
    writer = csv.writer(results_file)
    writer.writerow(
        ["simulation", "algorithm", "success", "steps", "path_cost", "stores_visited"]
    )

    for sim_file in tqdm(sorted(os.listdir("simulations"), key=lambda s: int(s[4:8]))):
        sim_path = f"simulations/{sim_file}"           # ← NEW LINE

        # Load once to extract the trigger store
        meta_env  = MallEnvironment.from_json(sim_path)
        trigger   = meta_env.stores[meta_env.goal_store_trigger_index]

        for algo in ("astar", "dstarlite", "mgastar"):
            env = MallEnvironment.from_json(sim_path)  # fresh env per run

            # Planner & agent selection
            if algo == "astar":
                planner = AStarPlanner(trigger)
                agent   = AStarAgent(env, planner=planner)

            elif algo == "dstarlite":
                planner = DStarLitePlanner(trigger)
                agent   = DStarLiteAgent(env, planner=planner)

            elif algo == "mgastar":
                planner = MultiGoalAStarPlanner(env.stores)
                agent   = MultiGoalAStarAgent(
                    env, planner=planner, must_visit=trigger
                )

            # Run the episode
            path = run_episode(agent, env)
            steps       = len(path) - 1
            path_cost   = steps            # unit-cost grid
            success     = env.goal_reached
            visited_cnt = len(env.visited_stores)

            # Save per-run path
            out_csv = f"paths/{algo}/{sim_file.replace('.json', '.csv')}"
            with open(out_csv, "w", newline="") as f:
                csv.writer(f).writerows(path)

            # Aggregate results
            writer.writerow(
                [sim_file, algo, success, steps, path_cost, visited_cnt]
            )

print("All simulations complete – check results.csv for the summary.")
