from interfaces.nodes import Node

class Elevator(Node):
    def __init__(self, row, column, f_number=0):
        super().__init__(row, column, f_number, node_type="elevator")
        self.node_type = "elevator"
        self.name = f"Elevator-{f_number}-{row}-{column}"

    def get_neighbors(self):
        return []
