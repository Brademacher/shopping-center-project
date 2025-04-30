from environment import MallEnvironment
from algorithms.astar import AStarPlanner
from algorithms.dstarlite import DStarLitePlanner
from algorithms.mgastar import MultiGoalAStarPlanner
from agents.astar_agent import AStarAgent
from agents.dstarlite_agent import DStarLiteAgent
from agents.mgastar_agent import MultiGoalAStarAgent

# Set which planner to test: "astar", "dstarlite", or "mgastar"
PLANNER_TYPE = "mgastar"

# Load environment
env = MallEnvironment.from_json("simulations/sim_0001.json")

# Choose planner and agent based on selection
if PLANNER_TYPE == "astar":
    goal_index = env.goal_store_trigger_index
    if goal_index is not None and 0 <= goal_index < len(env.stores):
        goal = env.stores[goal_index]
        planner = AStarPlanner(goal)
        agent = AStarAgent(env, planner=planner)
    else:
        raise ValueError("Invalid or missing goal store index.")

elif PLANNER_TYPE == "dstarlite":
    goal_index = env.goal_store_trigger_index
    if goal_index is not None and 0 <= goal_index < len(env.stores):
        goal = env.stores[goal_index]
        planner = DStarLitePlanner(goal)
        agent = DStarLiteAgent(env, planner=planner)
    else:
        raise ValueError("Invalid or missing goal store index.")

elif PLANNER_TYPE == "mgastar":
    planner = MultiGoalAStarPlanner(env.stores)
    agent = MultiGoalAStarAgent(env, planner=planner)

else:
    raise ValueError("Invalid PLANNER_TYPE. Use 'astar', 'dstarlite', or 'mgastar'.")

# Run simulation
while agent.step():
    pass

# Print results
print("\n🎯 Goal reached:", env.goal_reached)
print("📍 Total steps:", len(agent.path))
print("💰 Total cost:", round(agent.cost, 2))
print("🏪 Stores visited:", len(env.visited_stores))
