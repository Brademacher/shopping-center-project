def compute_path_cost(path):
    """
    Given a list of connected Node’s, sum up the edge weights
    between consecutive nodes.
    """
    cost = 0.0
    for a, b in zip(path, path[1:]):
        # find the neighbor‐link from a to b
        for link in a.get_neighbors():
            if link.node is b:
                cost += link.weight
                break
    return cost