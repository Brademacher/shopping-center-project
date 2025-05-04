from typing import List
from nodecomponents.neighbors import Neighbor

class Node:
    
    def __init__(self, row: int, column: int, f_number: int = 0, name: str = "", node_type: str = "generic"):
        self.row = row
        self.column = column
        self.f_number = f_number
        self.name = name  
        self.node_type = node_type  # e.g., "store", "elevator", "hallway"
        self.visited = False
        self.neighbors: List[Neighbor] = []

    def add_neighbor(self, direction: str, node: "Node", weight: float = 1.0):
        self.neighbors.append(Neighbor(direction, node, weight = 1.0))

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
