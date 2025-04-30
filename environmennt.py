import random

# Building 3D environment for agent testing #
class MallEnvironment:
    def __init__(self, length, width, floor):
        self.length = length
        self.width = width
        self.floor = floor
        self.grid = self.__create__empty__grid()

# Creating empty grid for environment #
    def __create__empty__grid(self):
        return [[[0 for i in range(self.width)] for j in range(self.length)] for k in range(self.floor)]

# Printing out grid for environment #
    def print_floor(self, floorIndex):
        if 0 <= floorIndex < self.floor:
            print(f"Floor {floorIndex}:")
            for row in self.grid[floorIndex]:
                print(" ".join(str(cell) for cell in row))
        else:
            print("Invalid floor index. Please choose a valid floor.")

# TODO Add stores in random perimeter spaces #
# TODO Add elevators in random perimeter spaces #
# TODO Add escalators in random perimeter spaces #
# TODO Add random obstacles to the environment grid #
# TODO Print function for all floors in the environment #
# TODO build a function for A* that has shows neighbors #

# Testing the environment class #
if __name__ == "__main__":
    mall = MallEnvironment(5, 7, 3)
    mall.print_floor(0)  # Print the first floor of the mall
    print("Mall environment created with dimensions:", mall.length, "x", mall.width, "x", mall.floor)