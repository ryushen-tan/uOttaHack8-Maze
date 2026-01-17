import osmnx as ox
from matplotlib import pyplot as plt

class Location:
    def __init__(self, place):
        self.G = ox.graph_from_place(place, network_type='drive')
    
    def get_nodes(self) -> list[tuple[float, float]]:
        return [(data['x'], data['y']) for _, data in self.G.nodes.items()]

    def get_node_position(self, node_data: dict) -> tuple[float, float]:
        return (node_data['x'], node_data['y'])

    def get_edges(self):
        edges = self.G.edges(keys=True, data=True)
        return [(self.get_node_position(self.G.nodes[u]), self.get_node_position(self.G.nodes[v])) for u, v, _, _ in edges]
    
    def plot_location(self):
        edges = self.get_edges()

        for edge in edges:
            start, end = edge
            x = (start[0], end[0])
            y = (start[1], end[1])
            plt.plot(x, y, color='blue')

        plt.grid(True)
        plt.show()