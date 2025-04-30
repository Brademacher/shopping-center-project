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

    for i, filename in enumerate(sorted(os.listdir("simulations"))):
        if filename.endswith(".json"):
            path = os.path.join("simulations", filename)
            env = MallEnvironment.from_json(path)

            # ✅ Use the goal store to create an A* planner
            goal_index = env.goal_store_trigger_index
            if goal_index is not None and 0 <= goal_index < len(env.stores):
                goal = env.stores[goal_index]
                planner = AStarPlanner(goal)
            else:
                planner = None

            # ✅ Create the agent using the planner
            agent = MallAgent(env, planner=planner)

            print(f"📦 Running simulation: {filename}")

            while agent.step():
                pass

            writer.writerow({
                "simulation": filename,
                "goal_reached": env.goal_reached,
                "steps": len(agent.path),
                "cost": round(agent.cost, 2),
                "stores_visited": len(env.visited_stores)
            })

            # ✅ Flush the file every 100 simulations
            if i % 100 == 0:
                csvfile.flush()
                tqdm.write(f"💾 Flushed after {i} simulations")

            tqdm.write(f"✓ {filename} — Goal: {env.goal_reached}, Steps: {len(agent.path)}, Cost: {round(agent.cost, 2)}, Stores: {len(env.visited_stores)}")
