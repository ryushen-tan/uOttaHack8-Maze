import osmnx as ox
from matplotlib import pyplot as plt
from typing import Union

from enum import Enum

# ox.settings.max_query_area_size = 50 * 1000 * 1000  # 50 km² in square meters
class RoadPriority(Enum):
    MOTORWAY_LINK = 0
    MOTORWAY = 0
    TRUNK = 1
    PRIMARY = 2
    SECONDARY = 3
    TERTIARY = 4
    RESIDENTIAL = 5
    UNCLASSIFIED = 6

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
        
        nodes = ox.graph_to_gdfs(self.G, edges=False)
        
        self.most_left  = nodes.geometry.x.min() # West (Longitude)
        self.most_down  = nodes.geometry.y.min() # South (Latitude)
        self.most_right = nodes.geometry.x.max() # East
        self.most_up    = nodes.geometry.y.max() # North

    def get_cache_name(self): 
        return f"map_{self.most_down:.4f}_{self.most_left:.4f}_{self.most_up:.4f}_{self.most_right:.4f}.csv"
    
    def get_nodes(self) -> list[tuple[float, float]]:
        return [(data['x'], data['y']) for _, data in self.G.nodes.items()]

    def get_node_position(self, node_data: dict) -> tuple[float, float]:
        return (node_data['x'], node_data['y'])

    def get_edges(self) -> list[tuple[tuple[float, float], tuple[float, float], bool, RoadPriority]]:
        edges = self.G.edges(keys=True, data=True)

        graph_edges = []
        for u, v, _, data in edges:
            oneway = True
            road_type: RoadPriority = RoadPriority.UNCLASSIFIED
            if 'oneway' in data.keys() and isinstance(data['oneway'], bool):
                oneway = data['oneway']

            if 'highway' in data.keys() and isinstance(data['highway'], str):
                road_type = self.parse_road_priority(data['highway'])

            graph_edges.append((self.get_node_position(self.G.nodes[u]), self.get_node_position(self.G.nodes[v]), oneway, road_type))
        
        return graph_edges
    
    def plot_location(self):
        edges = self.get_edges()

        for edge in edges:
            start, end, oneway, _ = edge

            x = (start[0], end[0])
            y = (start[1], end[1])
            plt.plot(x, y, color= "red" if oneway else "blue")

        plt.grid(True)
        plt.show()

    def parse_road_priority(self, highway: str) -> RoadPriority:
        match highway: 
            case 'motorway': 
                return RoadPriority.MOTORWAY
            case 'motorway_link': 
                return RoadPriority.MOTORWAY_LINK
            case 'trunk':
                return RoadPriority.TRUNK
            case 'primary':
                return RoadPriority.PRIMARY
            case 'secondary':
                return RoadPriority.SECONDARY
            case 'tertiary':
                return RoadPriority.TERTIARY
            case 'residential':
                return RoadPriority.RESIDENTIAL
            case 'unclassified':
                return RoadPriority.UNCLASSIFIED
            case _:
                return RoadPriority.UNCLASSIFIED