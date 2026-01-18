import random
from Graph import Graph
from Node import Node
from Edge import Edge
from Location import Location
from Worker import Worker

class World:
    def __init__(self, location: Location, num_workers: int = 10):
        self.graph = Graph()
        self.workers: list[Worker] = []

        for edge in location.get_edges():
            start = edge[0]
            end = edge[1]
            oneway = edge[2]
            priority = edge[3]

            self.graph.add_edge(Edge(Node(start[0], start[1]), Node(end[0], end[1]), oneway, priority))
        
        for _ in range(num_workers):
            self.workers.append(Worker(self.graph))
    
    def play(self):
        for worker in self.workers:
            worker.play()
    
    def is_finished(self) -> bool:
        return self.graph.clean_ratio() >= 1