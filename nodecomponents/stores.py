from interfaces.nodes import Node

class Store(Node):
    def __init__(self, row: int, column: int, f_number: int = 0, name: str = "", has_goal_item: bool = False):
        super().__init__(row, column, f_number, name=name, node_type="store")
        self.has_goal_item = has_goal_item

    def contains_goal_item(self) -> bool:
        return self.has_goal_item