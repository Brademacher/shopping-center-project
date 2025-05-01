from mallcomponents.floor import Floor

class Mall:
    def __init__(self, name: str, floors: list[Floor]):
        self.name = name
        self.floors = floors

    def add_floor(self, floor: Floor):
        self.floors.append(floor)
