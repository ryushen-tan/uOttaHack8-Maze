from Graph import Graph, Node, Edge
import random, time

class Worker:
    def __init__(self, graph: Graph, spawn_node: Node = None):
        self.graph: Graph = graph
        self.position: Node = spawn_node if spawn_node is not None else random.sample(list(self.graph.nodes), 1)[0]
    
    def play(self):
        options = self.graph.find_neighbours(self.position)
        if len(options) < 1:
            back_ups = [e for e in self.graph.edges if e.end == self.position]
            if any(back_ups):
                self.position = random.sample(back_ups, 1)[0].start
            return

        dirty_neighbours = [(n, e) for n, e in options if not e.clean]
        options = dirty_neighbours if any(dirty_neighbours) else list(options)
        new_pos, edge = random.sample(options, 1)[0]
        self.position = new_pos
        edge.clean = True
        