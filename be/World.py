import random
from Graph import Graph
from Node import Node
from Edge import Edge
from Location import Location
from Worker import Worker
from SubGraph import generate_sub_graphs, plot_sub_graphs

class World:
    def __init__(self, location: Location, num_workers: int = 10):
        self.graph = Graph()
        for edge in location.get_edges():
            start = edge[0]
            end = edge[1]
            oneway = edge[2]
            priority = edge[3]

            self.graph.add_edge(Edge(Node(start[0], start[1]), Node(end[0], end[1]), oneway, priority))
        
        self.sub_graphs = generate_sub_graphs(self.graph)
        
        self.workers: list[Worker] = []
        for _ in range(num_workers):
            self.workers.append(Worker(self.graph))
    
    def plot_sub_graphs(self):
        plot_sub_graphs(self.sub_graphs)

    def play(self):
        for worker in self.workers:
            worker.play()
    
    def is_finished(self) -> bool:
        return self.graph.clean_ratio() >= 1