from interfaces.nodes import Node

class Neighbor():
    def __init__(self, direction: str, node: "Node"):
        self.direction = direction
        self.node = node