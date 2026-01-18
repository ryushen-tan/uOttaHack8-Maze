import os, random
from Graph import Graph
from Node import Node
from Edge import Edge
from Location import Location
from Worker import Worker
from SubGraph import generate_sub_graphs, plot_sub_graphs

class World:
    def __init__(self, location: Location, num_workers: int = 10):
        self.graph = Graph()
        
        #Make a cache every time World()
        location_name = getattr(location, 'name', 'default_location')
        csv_filename = f"{location_name}_cache.csv"

        full_cache_path = os.path.join("cached_graphs", csv_filename)

        #If we already have location's bounds in cache
        # if os.path.exists(full_cache_path):
        if False:
            print(f"Loading bounds from cache: {full_cache_path}")
            
            #Then use cached bounds
            self.graph.csv_to_graph(full_cache_path)
            
        else:
            #else: Generate new simulation and store bounds in cache
            print(f"No cache found. Generating new bounds and saving to: {full_cache_path}")

            for edge in location.get_edges():
                start = edge[0]
                end = edge[1]
                oneway = edge[2]
                priority = edge[3]

                self.graph.add_edge(Edge(Node(start[0], start[1]), Node(end[0], end[1]), oneway, priority))

            #store bounds in cache
            self.graph.graph_to_csv(csv_filename)
        
        self.sub_graphs = generate_sub_graphs(self.graph)
        
        self.workers: list[Worker] = []
        for i in range(num_workers):
            self.workers.append(Worker(i, self.graph, random.sample(self.sub_graphs, 1)[0], self.workers))

        for worker in self.workers:
            worker.setup_worker()
    
    def plot_sub_graphs(self):
        plot_sub_graphs(self.sub_graphs)

    def play(self):
        for worker in self.workers:
            worker.play()
    
    def is_finished(self) -> bool:
        return self.graph.clean_ratio() >= 1