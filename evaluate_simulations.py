import os
import csv
from environment import MallEnvironment
from algorithms.astar import AStarPlanner
from agent import MallAgent
from tqdm import tqdm

# Create output file
with open("results.csv", "w", newline="") as csvfile:
    fieldnames = ["simulation", "goal_reached", "steps", "cost", "stores_visited"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    sim_files = sorted(f for f in os.listdir("simulations") if f.endswith(".json"))

    for i, filename in enumerate(tqdm(sim_files, desc="Evaluating Simulations", unit="sim")):
        path = os.path.join("simulations", filename)
        env = MallEnvironment.from_json(path)

        goal_index = env.goal_store_trigger_index
        if goal_index is not None and 0 <= goal_index < len(env.stores):
            goal = env.stores[goal_index]
            planner = AStarPlanner(goal)
        else:
            planner = None

        agent = MallAgent(env, planner=planner)

        while agent.step():
            pass

        writer.writerow({
            "simulation": filename,
            "goal_reached": env.goal_reached,
            "steps": len(agent.path),
            "cost": round(agent.cost, 2),
            "stores_visited": len(env.visited_stores)
        })

        if i % 100 == 0:
            csvfile.flush()