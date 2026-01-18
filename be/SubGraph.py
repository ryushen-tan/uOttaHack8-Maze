from Graph import Graph, Edge, Node

Y_RANGE = 50
X_RANGE = Y_RANGE * 5

class SubGraphEdge:
    def __init__(self, edge: Edge, from_sub_graph, to_sub_graph):
        from SubGraph import SubGraph

        if not isinstance(from_sub_graph, SubGraph) or not isinstance(to_sub_graph, SubGraph):
            raise "ERROR: from_sub_graph or to_sub_graph is not of class type SubGraph!"

        self.edge = edge
        self.from_sub_graph = from_sub_graph
        self.to_sub_graph = to_sub_graph

class SubGraph(Graph):
    def __init__(self, id: int, sub_graphs: list):
        super().__init__()

        self.sub_graphs = sub_graphs
        self.sub_graph_edges: set[SubGraphEdge] = set()
        self.id = id

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
    
    def find_neighbours(self, node: Node) -> set[tuple[Node, Edge | SubGraphEdge]]:
        sub_graph_neighbours: set[tuple[Node, Edge | SubGraphEdge]] = super().find_neighbours(node)
        for e in self.sub_graph_edges:
            edge = e.edge
            if not edge.oneway:
                if edge.end == node:
                    sub_graph_neighbours.add((edge.start, e))
            
            if edge.start == node:
                sub_graph_neighbours.add((edge.end, e))
            
        return sub_graph_neighbours


# Static SubGraph Functions
def find_sub_graph_with_node(sub_graphs: list[SubGraph], node: Node) -> SubGraph:
    for sub_graph in sub_graphs:
        if node in sub_graph.nodes:
            return sub_graph
    
    return None

def generate_sub_graphs(graph: Graph) -> set[SubGraph]:
    sub_graphs: set[SubGraph] = set()
    sub_graph_id = 0
    sorted_x_nodes = sorted(graph.nodes, key=lambda n: n.x)
    num_x_sections = round(len(sorted_x_nodes) / X_RANGE)

    for x_sec_num in range(num_x_sections):
        x_section = sorted_x_nodes[x_sec_num * X_RANGE : (x_sec_num + 1) * X_RANGE]
        sorted_y_nodes = sorted(x_section, key=lambda n: n.y)
        num_y_sections = round(len(sorted_y_nodes) / Y_RANGE)
        for y_sec_num in range(num_y_sections):
            y_section = sorted_y_nodes[y_sec_num * Y_RANGE : (y_sec_num + 1) * Y_RANGE]
            sub_graph = SubGraph(sub_graph_id, sub_graphs)
            sub_graph_id += 1
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