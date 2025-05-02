from interfaces.nodes import Node


class Floor():

    def __init__(self, rows: int, columns: int, f_number: int = 0, auto_connect: bool = True):
        self.rows = rows
        self.columns = columns
        self.f_number = f_number
        self.grid = [[Node(i, j, self.f_number) for j in range(self.columns)] for i in range(self.rows)]

        if auto_connect:
            self.connect_nodes()

    def connect_nodes(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if i > 0:
                    self.grid[i][j].add_neighbor("up", self.grid[i - 1][j])
                if i < self.rows - 1:
                    self.grid[i][j].add_neighbor("down", self.grid[i + 1][j])
                if j > 0:
                    self.grid[i][j].add_neighbor("left", self.grid[i][j - 1])
                if j < self.columns - 1:
                    self.grid[i][j].add_neighbor("right", self.grid[i][j + 1])

    def get_node(self, row: int, column: int) -> Node:
        if 0 <= row < self.rows and 0 <= column < self.columns:
            return self.grid[row][column]
        else:
            raise IndexError("Node coordinates out of bounds")


# TESTING PURPOSES ONLY #
if __name__ == "__main__":

    floor = Floor(rows=4, columns=5, f_number=1)

    print(f"Floor {floor.f_number} layout:")
    for row in floor.grid:
        row_str = " | ".join(f"({n.row},{n.column},{n.f_number})" for n in row)
        print(row_str)
