from World import World, Location
import time

loc = Location("Ottawa, Canada")

for u, v, k, data in loc.G.edges(keys=True, data=True):
    print(data)
    break
    