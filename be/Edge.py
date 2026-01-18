import math

from Node import Node
from Location import RoadPriority

class Edge:
    def __init__(self, start: Node, end: Node, oneway: bool = True, priority: RoadPriority = RoadPriority.UNCLASSIFIED):
        self.start = start
        self.end = end
        self.oneway = False
        self.priority = priority
        self.clean = False
        self.length: float = math.sqrt(math.pow(end.x - start.x, 2)) + math.sqrt(math.pow(end.y - start.y, 2))

    def vectorize(self) -> tuple[float, float, float, float, float, float]:
        return (self.start.x, self.start.y, self.end.x, self.end.y, float(self.priority.value), 1 if self.clean else 0)
    
    def __eq__(self, other):
        if isinstance(other, Edge):
            return (self.start == other.start or self.start == other.end) and (self.end == other.start or self.end == other.end)
        return False

    def __hash__(self):
        return hash((self.start, self.end))

    def __str__(self):
        return f'{{{self.start}, {self.end})}}'