from mallcomponents.floor import Floor

class Mall:
    def __init__(self, num_floors: int, rows: int, columns: int):
        self.floors = [Floor(rows, columns, f_number=i) for i in range(num_floors)]

    def get_all_stores(self):
        """Returns a flat list of all Store nodes across all floors."""
        return [store for floor in self.floors for store in floor.stores]

    def get_start_node(self):
        """Returns the first non-None start node found (assumes one start point)."""
        for floor in self.floors:
            if floor.start_node:
                return floor.start_node
        return None
    