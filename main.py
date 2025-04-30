import json
from environment import MallEnvironment
from agent import MallAgent

env = MallEnvironment.from_json("simulations/sim_0001.json")
agent = MallAgent(env)

while agent.step():
    pass

print("Goal reached:", env.goal_reached)
print("Total steps:", len(agent.path))
print("Total cost:", agent.cost)