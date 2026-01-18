from World import World, Location
from SubGraph import Y_RANGE
from Agent import DQNAgent
from Game import Game
import time

agent = DQNAgent(
    state_dim=(Y_RANGE ** 2) * 6 + 100 * 2 + 4 * 2,
    action_dim=4
)

place = "Kanata, Ontario, Canada"
display = Game(None)

for episode in range(500):
    world = World(Location(place))
    display.reset(world)
    timer = time.time()
    done = False
    total_reward = 0

    while not world.is_finished():
        for worker in world.workers:
            action = agent.act(worker.state)
            next_state, reward, done = worker.play(action)

            agent.remember(worker.state, action, reward, next_state, done)
            agent.train()

            worker.state = worker.get_state()
            total_reward += reward
            display.update()
        
        if time.time() - timer > 5:
            timer = time.time()
            print("Done: %", world.graph.clean_ratio() * 100)
        
    print(f'Episode {episode}, Reward: {total_reward}')

display.quit()