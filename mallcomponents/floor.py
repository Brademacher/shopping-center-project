from interfaces.nodes import Node
from interfaces.edges import Edge

class Floor(Node, Edge):
    def __init__(self, rows: int, columns: int):
        self.rows = rows
        self.columns = columns