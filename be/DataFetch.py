import osmnx as ox
from matplotlib import pyplot as plt
from typing import Union


ox.settings.max_query_area_size = 50 * 1000 * 1000  # 50 km² in square meters

class Location:
    def __init__(self, place: Union[str, list] = None, bounds: list = None):
        if bounds is not None:
            min_lat, max_lat, min_lon, max_lon = bounds
            # OSMNX graph_from_bbox takes bbox as tuple: (left, bottom, right, top)
            # which is (min_lon, min_lat, max_lon, max_lat) in lat/lon coordinates
            bbox = (min_lon, min_lat, max_lon, max_lat)
            self.G = ox.graph_from_bbox(bbox, network_type='drive')
        elif place is not None:
            self.G = ox.graph_from_place(place, network_type='drive')
        else:
            raise ValueError("Either 'place' or 'bounds' must be provided")
    
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