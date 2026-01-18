from Node import Node
from Edge import Edge

import csv
import os

from Location import RoadPriority, Location

class Graph:
    def __init__(self):
        self.nodes: set[Node] = set()
        self.edges: set[Edge] = set()

        self.most_left = float('inf')
        self.most_right = float('-inf')
        self.most_down = float('inf')
        self.most_up = float('-inf')

    def add_edge(self, edge: Edge):
        self.edges.add(edge)

        self.nodes.add(edge.start)
        self.nodes.add(edge.end)

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
    
    def find_neighbours(self, node: Node) -> set[tuple[Node, Edge]]:
        neighbours = set()
        for edge in self.edges:
            if not edge.oneway:
                if edge.end == node:
                    neighbours.add((edge.start, edge))
            
            if edge.start == node:
                neighbours.add((edge.end, edge))

        return neighbours

    def clean_ratio(self) -> float:
        return len([e for e in self.edges if e.clean]) / len(self.edges)

    def width(self) -> float:
        return self.most_right - self.most_left
    
    def height(self) -> float:
        return self.most_up - self.most_down
    
    def relative_position(self, node: Node) -> tuple[float, float]:
        return ((node.x - self.most_left) / self.width(), (node.y - self.most_down) / self.height())

    def to_dict(self):
        return {
            'nodes': [{'x': node.x, 'y': node.y} for node in self.nodes],
            'edges': [
                {
                    'start': {'x': edge.start.x, 'y': edge.start.y},
                    'end': {'x': edge.end.x, 'y': edge.end.y},
                    'length': edge.length
                }
                for edge in self.edges
            ],
            'bounds': {
                'left': self.most_left,
                'right': self.most_right,
                'down': self.most_down,
                'up': self.most_up
            }
        }

    def __str__(self):
        nodes_str = [str(node) for node in self.nodes]
        edges_str = [str(edge) for edge in self.edges]
        return f'nodes: {str(nodes_str)}\nedges: {str(edges_str)}'

    def graph_to_csv(self, location) -> str:
        folder_name = "cached_graphs"

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        file_name = Location.get_cache_name(location)

        full_path = os.path.join(folder_name, file_name)

        with open(full_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['start_x', 'start_y', 'end_x', 'end_y', 'most_left', 'most_right', 'most_down', 'most_up', 'clean', 'priority', 'oneway'])

            for edge in self.edges:
                writer.writerow([
                    edge.start.x, edge.start.y,
                    edge.end.x, edge.end.y,
                    self.most_left, self.most_right, self.most_down, self.most_up, 
                    edge.clean, edge.priority.value, edge.oneway
                ])
    
    def csv_to_graph(self, file_path: str):
        print("loading graph from csv...")

        self.edges = set()
        self.nodes = set()

        node_map = {}

        try: 
            with open(file_path, 'r') as f: 
                reader = csv.DictReader(f)

                for row in reader: 
                    sx, sy = float(row['start_x']), float(row['start_y'])
                    ex, ey = float(row['end_x']), float(row['end_y'])
                    
                    if (sx, sy) not in node_map:
                        node_map[(sx, sy)] = Node(sx, sy)
                    
                    start_node = node_map[(sx, sy)]

                    if (ex, ey) not in node_map:
                        node_map[(ex, ey)] = Node(ex, ey)
                        
                    end_node = node_map[(ex, ey)]

                    self.most_left  = float(row['most_left'])
                    self.most_right = float(row['most_right'])
                    self.most_down  = float(row['most_down'])
                    self.most_up    = float(row['most_up'])

                    is_clean = row['clean'].lower() == 'true'
                    priority_val = int(row['priority'])
                    is_oneway = row['oneway'].lower() == 'true'

                    edge = Edge(start_node, end_node)
                    edge.clean = is_clean
                    edge.priority = RoadPriority(priority_val)
                    edge.oneway = is_oneway
                    
                    self.add_edge(edge)

                print(f"✅ Graph loaded! ({len(self.edges)} edges, {len(self.nodes)} nodes)")
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"Error parsing CSV: {e}")