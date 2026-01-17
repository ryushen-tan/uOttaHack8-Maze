import osmnx as ox
from matplotlib import pyplot as plt

class Location:
    def __init__(self, place):
        self.G = ox.graph_from_place(place, network_type='drive')
    
    def get_nodes(self) -> list[tuple[float, float]]:
        return [(data['x'], data['y']) for _, data in self.G.nodes.items()]

    def get_node_position(self, node_data: dict) -> tuple[float, float]:
        return (node_data['x'], node_data['y'])

    def get_edges(self) -> list[tuple[tuple[float, float], tuple[float, float], bool]]:
        edges = self.G.edges(keys=True, data=True)

        graph_edges = []
        for u, v, _, data in edges:
            oneway = True
            if 'oneway' in data.keys() and isinstance(data['oneway'], bool):
                oneway = data['oneway']
            graph_edges.append((self.get_node_position(self.G.nodes[u]), self.get_node_position(self.G.nodes[v]), oneway))
        
        return graph_edges
    
    def plot_location(self):
        edges = self.get_edges()

        for edge in edges:
            start, end, oneway = edge
            x = (start[0], end[0])
            y = (start[1], end[1])
            plt.plot(x, y, color= "red" if oneway else "blue")

        plt.grid(True)
        plt.show()