from interfaces.edges import Edge

class Neighbor(Edge):
    def __init__(self, direction: str, node: "Node", weight: float = 1.0):
        super().__init__(weight)
        self.direction = direction
        self.node = node