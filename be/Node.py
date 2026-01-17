
class Node:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def position(self) -> tuple[float, float]:
        return self.x, self.y

    def __eq__(self, other):
        if other is Node:
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f'({self.x}, {self.y})'