from Graph import Graph, Node, Edge
import random

class Worker:
    def __init__(self, graph: Graph, spawn_node: Node = None):
        self.graph: Graph = graph
        self.position: Node = spawn_node if spawn_node is not None else random.sample(self.graph.nodes, 1)[0]
    
    def play(self):
        options = self.graph.find_neighbours(self.position)
        dirty_neighbours = [(n, e) for n, e in options if not e.clean]
        options = dirty_neighbours if any(dirty_neighbours) else options
        new_pos, edge = random.sample(options, 1)[0]
        self.position = new_pos
        edge.clean = True
        