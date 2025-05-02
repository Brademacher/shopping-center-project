from typing import List
from nodecomponents.neighbors import Neighbor

class Node:
    
    def __init__(self, row: int, column: int, floor: int = 0):
        self.row = row
        self.column = column
        self.floor = floor
        self.visited = False
        self.neighbors: List[Neighbor] = []

    def add_neighbor(self, direction: str, node: "Node"):
        self.neighbors.append(Neighbor(direction, node))

    def remove_neighbor(self, direction: str):
        if direction in self.neighbors:
            self.neighbors.remove(direction)

    def get_neighbors(self) -> List[Neighbor]:
        return self.neighbors
        


# TESTING PURPOSES ONLY #
if __name__ == "__main__":
    a = Node("A", 0, 0)
    b = Node("B", 0, 1)
    
    a.add_neighbor("right", b, weight=2.0)

    print(f"{a.name}'s neighbor to the right: {a.neighbors[0].node.name}")
    print(f"Edge weight: {a.neighbors[0].weight}")