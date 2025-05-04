from typing import List
from nodecomponents.neighbors import Neighbor

class Node:
    
    def __init__(self, row: int, column: int, f_number: int = 0, name: str = "", node_type: str = "generic"):
        self.row = row
        self.column = column
        self.f_number = f_number
        self.name = name  # e.g., "Starbucks"
        self.node_type = node_type  # e.g., "store", "elevator", "hallway"
        self.visited = False
        self.neighbors: List[Neighbor] = []

    def add_neighbor(self, direction: str, node: "Node", weight: float = 1.0):
        self.neighbors.append(Neighbor(direction, node, weight = (0 if node.node_type == "obstacle" else 1)))

    def remove_neighbor(self, direction: str):
        self.neighbors = [n for n in self.neighbors if n.direction != direction]

    def get_neighbors(self) -> List[Neighbor]:
        return self.neighbors
    

    ## For A* algorithm, comparison methods for the priority queue    
    def __lt__(self, other):
        return (self.row, self.column, self.f_number) < (other.row, other.column, other.f_number)
    
    def __eq__(self, other):
        return (self.row, self.column, self.f_number) == (other.row, other.column, other.f_number)

    def __hash__(self):
        return hash((self.row, self.column, getattr(self, 'f_number', 0)))


# TESTING PURPOSES ONLY #
if __name__ == "__main__":
    a = Node(row=0, column=0, name="A")
    b = Node(row=0, column=1, name="B")
    
    a.add_neighbor("right", b)

    print("\nEquality and hashing test:")
    n1 = Node(row=1, column=2, f_number=0)
    n2 = Node(row=1, column=2, f_number=0)
    n3 = Node(row=2, column=2, f_number=0)

    print("n1 == n2:", n1 == n2)             # True
    print("n1 == n3:", n1 == n3)             # False
    print("Hash of n1:", hash(n1))           # Same as n2
    print("Hash of n2:", hash(n2))           # Same as n1
    print("Hash of n3:", hash(n3))           # Different
    print("n1 < n3:", n1 < n3)               # True (row 1 < row 2)

    print("\nTesting set behavior:")
    node_set = {n1, n2, n3}
    for node in sorted(node_set):
        print(f"Node at ({node.row}, {node.column}, floor {node.f_number})")
