from interfaces.nodes import Node

class Stairs(Node):
    def __init__(self, row, column, f_number):
        super().__init__(row, column, f_number, node_type="stairs")
