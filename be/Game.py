import pygame
from World import World, Node, Edge, Location, Graph
import time

start_time = time.time()
place = "New York City, NY, USA"
print(f"Processing graph for {place}...")
world = World(Location(place))
print(f"Processing graph complete in {time.time() - start_time} seconds!")
print((world.graph.width(), world.graph.height()))

pygame.init()
screen = pygame.display.set_mode((1280, 720))
scale = 1.0
clock = pygame.time.Clock()
running = True
dt = 0

def grid_to_screen(node: Node) -> tuple[float, float]:
    relative_pos = world.graph.relative_position(node)
    return ((relative_pos[0]) * screen.get_width(), (1 - relative_pos[1]) * screen.get_height())


def draw_node(node: Node):
    pygame.draw.circle(screen, "white", grid_to_screen(node), 1)


def draw_edge(edge: Edge):
    pygame.draw.line(screen, "blue", grid_to_screen(edge.start), grid_to_screen(edge.end), 1)

def draw_graph(graph: Graph):
    for e in graph.edges:
        draw_edge(e)

    for n in graph.nodes:
        draw_node(n)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")

    draw_graph(world.graph)

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
