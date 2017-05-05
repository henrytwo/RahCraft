from random import *
from pickle import *
import numpy as np

# Code to trigger Syed
with open('block', 'r') as block_lookup:
    block_list = block_lookup.read().strip().split('\n')

block_list = [block.split(' // ') for block in block_list]

block_lookup = {block_list[i][0]: (i) for i in range(len(block_list))}


def generate_tree(bx,by,world):

    height = randint(4,6)

        
    for y in range(height):
        world[bx][by-y] = block_lookup["Wood"]


    for x in range(randint(3,5)):
        for y in range(randint(2,4)):
            world[bx - x//2][by - y - height] = block_lookup["Leaves"]
            world[bx + x//2][by - y - height] = block_lookup["Leaves"]

    return world




# ----- Game World Construction Function
def generate_world(world_seed,maxHeight,minX,maxX,w,h):

    """ Creates a world object randomly generated using a user-inputted seed. """

    # Set the initial seed for the random module (random.seed())
    seed(world_seed)
    
    # Create a blank map (2D list filled with '0' strings
    world = [[0 for y in range(h)] for x in range(w)]
    # Generates the random values for the terrain construction
    terrain = [randrange(10) + 40 for _ in range(w)]

    # ----- Construct tdsadhe Terrain
    # Counter that changes dynamically to check through all blocks in the terrain list
    cur_pos = 0
    # Runs through all the generated numbers in a while loop
    while cur_pos < len(terrain):

        # print(".", end="")

        # Check to see if terrain gap is too large

        if abs(terrain[cur_pos] - terrain[cur_pos - 1]) > maxHeight:  # if terrain gap is larger than threshhold (too big)

            for n in range(randint(minX,maxX)):
                # Insert a new value into the terrain list between the values that are too far apart
                terrain.insert(cur_pos, (terrain[cur_pos] + terrain[cur_pos - 1]) // 2)
            
        else:  # Difference between the two blocks is not too big

            # Check next block
            cur_pos += 1



    # ----- Transfer Terrain To Empty World
    # Run through every space in the empty world
    for x in range(len(world)):  # runs through each level
        for y in range(len(world[x])):  # runs through each individual space

            # Generates structures
            if y > terrain[x]:
                if y - terrain[x] == 1:
                    world[x][y] = block_lookup["Grass"]

                    if randint(0,10) == 0 and x + 10 < w:
                        world = generate_tree(x,y - 1,world)

                elif y - terrain[x] < randint(3,8):
                    world[x][y] = block_lookup["Dirt"]

                else:
                    world[x][y] = block_lookup["Stone"]

                if y > 92 or y > 87 and randint(0,3) == 0:
                    world[x][y] = block_lookup["Bed Rock"]


    # Return the world object for use
    return np.array(world)

