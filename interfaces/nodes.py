from typing import Dict

class Node:
    
    def __init__(self, name: str, row: int, column: int, floor: int = 0):
        self.name = name
        self.row = row
        self.column = column
        self.floor = floor
        self.visited = False
        self.neighbors: Dict[str,"Node"] = {}

    def add_neighbor(self, direction: str, node: "Node"):
        self.neighbors[direction] = node

    def remove_neighbor(self, direction: str):
        if direction in self.neighbors:
            del self.neighbors[direction]