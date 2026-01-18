import pygame
from World import World, Node, Edge, Location, Worker
from SubGraph import SubGraphEdge
from Location import RoadPriority
import time, random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

class Game:
    def __init__(self, world: World | None):
        self.offset = (0.0, 0.0)
        self.offset_amount = 35
        self.scale = 1.0
        self.world = world

    def grid_to_screen(self, node: Node) -> tuple[float, float]:
        relative_pos = self.world.graph.relative_position(node)
        return (((relative_pos[0]) * screen.get_width() * self.scale) - (self.offset[0] * self.scale), ((1 - relative_pos[1]) * screen.get_height() * self.scale) - (self.offset[1] * self.scale))

    def priorty_color(self, priorty: RoadPriority) -> str:
        match priorty:
            case RoadPriority.MOTORWAY_LINK:
                return '#8B0000'
            case RoadPriority.MOTORWAY:
                return '#8B0000'
            case RoadPriority.TRUNK:
                return '#FF0000'
            case RoadPriority.PRIMARY:
                return '#FF8C00'
            case RoadPriority.SECONDARY:
                return '#FFD700'
            case RoadPriority.TERTIARY:
                return '#87CEEB'
            case RoadPriority.RESIDENTIAL:
                return '#D3D3D3'
            case RoadPriority.UNCLASSIFIED:
                return '#D3D3D3'

    def node_in_scale_range(self, node: Node) -> bool:
        relative_pos = self.world.graph.relative_position(node)
        return (self.offset[0] / screen.get_width()) <= relative_pos[0] <= (self.offset[0] / screen.get_width()) + (1 / self.scale) and (self.offset[1] / screen.get_height()) <= 1 - relative_pos[1] <= (self.offset[1] / screen.get_height()) + (1 / self.scale)

    def draw_node(self, node: Node):
        if self.node_in_scale_range(node):
            pygame.draw.circle(screen, "blue", self.grid_to_screen(node), 1.5)

    def reset(self, world: World):
        self.world = world
        self.color_dict = self.sub_graph_color_dict(self.world)
        self.scale = 1
        self.offset = (0, 0)

    def draw_edge(self, edge: Edge, color: tuple[float, float, float] | str):
        if self.node_in_scale_range(edge.start) or self.node_in_scale_range(edge.end):
            # final_color = priorty_color(edge.priority) if not edge.clean else "green"
            final_color = color if not edge.clean else "green"
            size = 1 if edge.oneway else 2
            pygame.draw.line(screen, final_color, self.grid_to_screen(edge.start), self.grid_to_screen(edge.end), size)

    def draw_sub_graph_edge(self, edge: SubGraphEdge):
        self.draw_edge(edge.edge, "black")

    def draw_worker(self, worker: Worker):
        if self.node_in_scale_range(worker.position):
            pygame.draw.circle(screen, "red", self.grid_to_screen(worker.position), 3)

    def draw_world(self, world: World):
        for sub_graph in world.sub_graphs:
            color = self.color_dict[sub_graph.id]
            for e in sub_graph.edges:
                self.draw_edge(e, color)
            for e in sub_graph.sub_graph_edges:
                self.draw_sub_graph_edge(e)
            for n in sub_graph.nodes:
                self.draw_node(n)
        
        for worker in world.workers:
            self.draw_worker(worker)

    def sub_graph_color_dict(self, world: World) -> dict[int, tuple[float, float, float]]:
        colors = {}
        for sub_graph in world.sub_graphs:
            colors[sub_graph.id] = (random.random() * 255, random.random() * 255, random.random() * 255)
        
        return colors

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.scale *= 2
                    self.offset_amount /= 2
                elif event.key == pygame.K_o:
                    self.scale /= 2
                    self.offset_amount *= 2
                elif event.key == pygame.K_RIGHT:
                    self.offset = (self.offset[0] + self.offset_amount, self.offset[1])
                elif event.key == pygame.K_LEFT:
                    self.offset = (self.offset[0] - self.offset_amount, self.offset[1])
                elif event.key == pygame.K_UP:
                    self.offset = (self.offset[0], self.offset[1] - self.offset_amount)
                elif event.key == pygame.K_DOWN:
                    self.offset = (self.offset[0], self.offset[1] + self.offset_amount)

        screen.fill("white")

        if self.world is not None:
            self.draw_world(self.world)
            
            pygame.display.set_caption(f'Clean: %{self.world.graph.clean_ratio() * 100}')

        pygame.display.flip()
        dt = clock.tick(60) / 1000
    
    def quit(self):
        pygame.quit()
