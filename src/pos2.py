class Pos2:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
    
    def __getitem__(self, i: int) -> int:
        if i == 0: return self.x
        elif i == 1: return self.y
        else: raise IndexError()

    def __add__(self, other) -> 'Pos2':
        return Pos2(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> 'Pos2':
        return Pos2(self.x - other.x, self.y - other.y)
