from World import World, Location

world = World(Location("Kanata, Ontario, Canada"))

print(len(world.sub_graphs))
world.plot_sub_graphs()