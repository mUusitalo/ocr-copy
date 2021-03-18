class Pos2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __getitem__(self, i: int):
        if i == 0: return self.x
        elif i == 1: return self.y
        else: raise IndexError()

    def __add__(self, other):
        return Pos2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pos2(self.x - other.x, self.y - other.y)
