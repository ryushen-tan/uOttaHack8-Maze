from Graph import Graph, Edge, Node

class SubGraph(Graph):
    def __init__(self, sub_graphs: list):
        super().__init__()

        self.sub_graphs = sub_graphs
        self.sub_graph_edges: set[SubGraphEdge] = set()

    def add_edges_to_sub_graph(self, graph: Graph):
        # internal edges
        self.add_edges([e for e in graph.edges if e.start in self.nodes and e.end in self.nodes])

        # external edges
        for e in graph.edges:
            if not e.oneway:
                if e.end in self.nodes and e.start not in self.nodes:
                    other = find_sub_graph_with_node(self.sub_graphs, e.start)
                    if other is not None:
                        self.sub_graph_edges.add(SubGraphEdge(e, other, self))
                        continue
            
            if e.start in self.nodes and e.end not in self.nodes:
                other = find_sub_graph_with_node(self.sub_graphs, e.end)
                if other is not None:
                    self.sub_graph_edges.add(SubGraphEdge(e, self, other))

class SubGraphEdge:
    def __init__(self, edge: Edge, from_sub_graph: SubGraph, to_sub_graph: SubGraph):
        self.edge = edge
        self.from_sub_graph = from_sub_graph
        self.to_sub_graph = to_sub_graph

# Static SubGraph Functions
def find_sub_graph_with_node(sub_graphs: list[SubGraph], node: Node) -> SubGraph:
    for sub_graph in sub_graphs:
        if node in sub_graph.nodes:
            return sub_graph
    
    return None

def generate_sub_graphs(graph: Graph) -> set[SubGraph]:
    sub_graphs: set[SubGraph] = set()
    sorted_x_nodes = sorted(graph.nodes, key=lambda n: n.x)
    x_node_size_range = 1000
    y_node_size_range = 200
    num_x_sections = round(len(sorted_x_nodes) / x_node_size_range)

    for x_sec_num in range(num_x_sections):
        x_section = sorted_x_nodes[x_sec_num * x_node_size_range : (x_sec_num + 1) * x_node_size_range]
        sorted_y_nodes = sorted(x_section, key=lambda n: n.y)
        num_y_sections = round(len(sorted_y_nodes) / y_node_size_range)
        for y_sec_num in range(num_y_sections):
            y_section = sorted_y_nodes[y_sec_num * y_node_size_range : (y_sec_num + 1) * y_node_size_range]
            sub_graph = SubGraph(sub_graphs)
            sub_graph.add_nodes(y_section)
            sub_graphs.add(sub_graph)
    
    # Calculate edges
    for sub_graph in sub_graphs:
        sub_graph.add_edges_to_sub_graph(graph)
    
    return sub_graphs

def plot_sub_graphs(sub_graphs: set[SubGraph]):
    import matplotlib.pyplot as plt
    import random

    for sub_graph in sub_graphs:
        color = (random.random(), random.random(), random.random())
        plt.scatter([n.x for n in sub_graph.nodes], [n.y for n in sub_graph.nodes], color=color, s=1, zorder=2)
        for e in sub_graph.edges:
            plt.plot((e.start.x, e.end.x), (e.start.y, e.end.y), color=color, zorder=1)
        for e in sub_graph.sub_graph_edges:
            edge = e.edge
            plt.plot((edge.start.x, edge.end.x), (edge.start.y, edge.end.y), color="black", zorder=1)
    
    plt.show()
    plt.waitforbuttonpress()