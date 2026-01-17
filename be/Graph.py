from Node import Node
from Edge import Edge

class Graph:
    def __init__(self):
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()

        self.most_left = float('inf')
        self.most_right = float('-inf')
        self.most_down = float('inf')
        self.most_up = float('-inf')

    def add_edge(self, edge: Edge):
        self.add_node(edge.start)
        self.add_node(edge.end)

        self.edges.add(edge)

    def add_node(self, node: Node):
        self.nodes.add(node)

        if node.x < self.most_left:
            self.most_left = node.x
        if node.x > self.most_right:
            self.most_right = node.x
        if node.y < self.most_down:
            self.most_down = node.y
        if node.y > self.most_up:
            self.most_up = node.y
    
    def width(self) -> float:
        return self.most_right - self.most_left
    
    def height(self) -> float:
        return self.most_up - self.most_down
    
    def relative_position(self, node: Node) -> tuple[float, float]:
        return ((node.x - self.most_left) / self.width(), (node.y - self.most_down) / self.height())

    def __str__(self):
        nodes_str = [str(node) for node in self.nodes]
        edges_str = [str(edge) for edge in self.edges]
        return f'nodes: {str(nodes_str)}\nedges: {str(edges_str)}'