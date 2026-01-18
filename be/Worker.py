from SubGraph import Node, SubGraph, Edge, SubGraphEdge, Y_RANGE, Graph
import random

class Worker:
    def __init__(self, id: int, graph: Graph, sub_graph: SubGraph, workers: list, spawn_node: Node = None):
        self.id = id
        self.workers: list[Worker] = workers
        self.graph = graph
        self.sub_graph: SubGraph = sub_graph
        self.position: Node = spawn_node if spawn_node is not None and spawn_node in sub_graph.nodes else random.sample(tuple(self.sub_graph.nodes), 1)[0]
    
    def setup_worker(self):
        self.current_actions = []
        self.state = self.get_state()
    
    def play(self, action):
        return self.apply_action(self.current_actions[action] if action < len(self.current_actions) else None)
    
    def get_state(self) -> tuple[float, ...]:
        workers = tuple([self.vectorize()] + [w.vectorize() for w in self.workers if w.id != self.id] + [(0, 0) for _ in range(100 - len(self.workers))])
        workers = tuple(x for sub in workers for x in sub)

        edges = tuple([e.vectorize() for e in self.sub_graph.edges] + [(0, 0, 0, 0, 0, 0) for _ in range((Y_RANGE ** 2) - len(self.sub_graph.edges))])
        edges = tuple(x for sub in edges for x in sub)

        actions = self.actions()
        actions = list(actions)

        if len(actions) > 4:
            actions = random.sample(actions, 4)
        
        self.current_actions = actions
        actions = tuple([(node.x, node.y) for node,  _ in actions] + [(0, 0) for _ in range(4 - len(actions))])
        actions = tuple(x for sub in actions for x in sub)

        return tuple(workers + edges + actions)

    
    def actions(self) -> set[tuple[Node, Edge | SubGraphEdge]]:
        return self.sub_graph.find_neighbours(self.position)

    def is_done(self) -> bool:
        return self.graph.clean_ratio() >= 1
        
    def apply_action(self, action: tuple[Node, Edge | SubGraphEdge] | None) -> tuple[tuple[float, ...], float, bool]:
        if action is None:
            return self.get_state(), -5, self.is_done()
        
        if isinstance(action[1], Edge):
            self.position = action[0]
            was_clean = action[1].clean
            action[1].clean = True
            return self.get_state(), -2 if was_clean else 7 - action[1].priority.value, self.is_done()
        
        elif isinstance(action[1], SubGraphEdge):
            self.sub_graph = action[1].to_sub_graph if self.position in action[1].from_sub_graph.nodes else action[1].from_sub_graph
            self.position = action[0]
            sub_graph_clean = self.sub_graph.clean_ratio() >= 1
            was_clean = action[1].edge.clean
            action[1].edge.clean = True
            return self.get_state(), 20 if sub_graph_clean else -10 if was_clean else 7 - action[1].edge.priority.value, self.is_done()

        else:
            raise "ERROR: Selected action is not of correct type!"

    def vectorize(self) -> tuple[float, float]:
        return (self.position.x, self.position.y)