import random

def assign_goal_item_to_store(stores: list):
    if stores:
        # Randomly choose a store from the list of stores
        goal_store = random.choice(stores)
        goal_store.has_goal_item = True
        print(f"Store {goal_store.name} now has the goal item!")

def is_goal_node(node, goal_nodes):
    return any(
        node.row == g.row and node.column == g.column and node.f_number == g.f_number
        for g in goal_nodes
    )