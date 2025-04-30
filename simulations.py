import os
from environment import MallEnvironment

# Create output directory if it doesn't exist
os.makedirs("simulations", exist_ok=True)

# Simulation parameters
NUM_SIMULATIONS = 1000
GRID_SIZE = (10, 10, 3)
NUM_STORES = 20
NUM_OBSTACLES = 10
NUM_ELEVATORS = 2
NUM_ESCALATORS = 3
GOAL_INDEX = 5  # 6th store visited ends simulation

for i in range(NUM_SIMULATIONS):
    env = MallEnvironment(
        length=GRID_SIZE[0],
        width=GRID_SIZE[1],
        floor=GRID_SIZE[2],
        num_stores=NUM_STORES,
        num_obstacles=NUM_OBSTACLES,
        num_elevators=NUM_ELEVATORS,
        num_escalators=NUM_ESCALATORS
    )
    env.set_goal_trigger_index(GOAL_INDEX)

    # Save to simulations/sim_0001.json, etc.
    filename = f"simulations/sim_{i:04d}.json"
    env.to_json(filename)

    if i % 100 == 0:
        print(f"Saved: {filename}")