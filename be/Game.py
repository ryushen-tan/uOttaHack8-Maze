import pygame
from World import World, Node, Edge, Location, Worker
from Location import RoadPriority
import time

start_time = time.time()
place = "Orleans, Ontario, Canada"
offset = (0.0, 0.0)
offset_amount = 35
scale = 1.0
print(f"Processing graph for {place}...")
world = World(Location(place), 10)
print("Number of Edges: ", len(world.graph.edges))
print(f"Processing graph complete in {time.time() - start_time} seconds!")

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

def grid_to_screen(node: Node) -> tuple[float, float]:
    relative_pos = world.graph.relative_position(node)
    return (((relative_pos[0]) * screen.get_width() * scale) - (offset[0] * scale), ((1 - relative_pos[1]) * screen.get_height() * scale) - (offset[1] * scale))

def priorty_color(priorty: RoadPriority) -> str:
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

def node_in_scale_range(node: Node) -> bool:
    relative_pos = world.graph.relative_position(node)
    return (offset[0] / screen.get_width()) <= relative_pos[0] <= (offset[0] / screen.get_width()) + (1 / scale) and (offset[1] / screen.get_height()) <= 1 - relative_pos[1] <= (offset[1] / screen.get_height()) + (1 / scale)

def draw_node(node: Node):
    if node_in_scale_range(node):
        pygame.draw.circle(screen, "white", grid_to_screen(node), 1)


def draw_edge(edge: Edge):
    if node_in_scale_range(edge.start) or node_in_scale_range(edge.end):
        color = priorty_color(edge.priority) if not edge.clean else "green"
        scale = 1 if edge.oneway else 2
        pygame.draw.line(screen, color, grid_to_screen(edge.start), grid_to_screen(edge.end), scale)

def draw_worker(worker: Worker):
    if node_in_scale_range(worker.position):
        pygame.draw.circle(screen, "red", grid_to_screen(worker.position), 3)

def draw_world(world: World):
    for e in world.graph.edges:
        draw_edge(e)

    for n in world.graph.nodes:
        draw_node(n)
    
    for w in world.workers:
        draw_worker(w)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                scale *= 2
                offset_amount /= 2
            elif event.key == pygame.K_o:
                scale /= 2
                offset_amount *= 2
            elif event.key == pygame.K_RIGHT:
                offset = (offset[0] + offset_amount, offset[1])
            elif event.key == pygame.K_LEFT:
                offset = (offset[0] - offset_amount, offset[1])
            elif event.key == pygame.K_UP:
                offset = (offset[0], offset[1] - offset_amount)
            elif event.key == pygame.K_DOWN:
                offset = (offset[0], offset[1] + offset_amount)

    screen.fill("black")

    world.play()
    draw_world(world)

    running = not world.is_finished()
    pygame.display.set_caption(f'Clean: %{world.graph.clean_ratio() * 100}')

    pygame.display.flip()
    dt = clock.tick(60) / 1000

pygame.quit()
