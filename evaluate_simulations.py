import os
import csv
from environment import MallEnvironment
from agent import MallAgent

# Create output file
with open("results.csv", "w", newline="") as csvfile:
    fieldnames = ["simulation", "goal_reached", "steps", "cost", "stores_visited"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for filename in sorted(os.listdir("simulations")):
        if filename.endswith(".json"):
            path = os.path.join("simulations", filename)
            env = MallEnvironment.from_json(path)
            agent = MallAgent(env)

            while agent.step():
                pass

            writer.writerow({
                "simulation": filename,
                "goal_reached": env.goal_reached,
                "steps": len(agent.path),
                "cost": round(agent.cost, 2),
                "stores_visited": len(env.visited_stores)
            })

            print(f"Evaluated {filename}")
