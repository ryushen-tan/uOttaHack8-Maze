import random

from Graph import Graph
from Node import Node
from Edge import Edge
from DataFetch import Location

class World:
    def __init__(self, location: Location):
        self.graph = Graph()

        for edge in location.get_edges():
            start = edge[0]
            end = edge[1]

            self.graph.add_edge(Edge(Node(start[0], start[1]), Node(end[0], end[1])))