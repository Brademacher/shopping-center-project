import json
from environment import MallEnvironment
from agent import MallAgent
from algorithms.astar import AStarPlanner  # ✅ Add this line

# Load environment from file
env = MallEnvironment.from_json("simulations/sim_0001.json")

# Set up A* planner using the goal store
goal_index = env.goal_store_trigger_index
if goal_index is not None and 0 <= goal_index < len(env.stores):
    goal = env.stores[goal_index]
    planner = AStarPlanner(goal)
else:
    planner = None

# Create agent using the planner
agent = MallAgent(env, planner=planner)

# Step through the simulation
while agent.step():
    pass

# Output final stats
print("Goal reached:", env.goal_reached)
print("Total steps:", len(agent.path))
print("Total cost:", round(agent.cost, 2))
print("Stores visited:", len(env.visited_stores))
