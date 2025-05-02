from interfaces.nodes import Node
from interfaces.edges import Edge

class Floor():

    def __init__(self, rows: int, columns: int, number: int = 0):
        self.rows = rows
        self.columns = columns
        self.number = number

    def build_floor(self):
        # Create a 2D array of nodes
        self.floor = [[Node(i, j, self.number) for j in range(self.columns)] for i in range(self.rows)]
