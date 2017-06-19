#world.py
#Generates a random world based on given seed

from random import *
import json
import numpy as np

#Import biomes
block_data = json.load(open("data/block.json"))

#Biome dictionary
block_lookup = {}

#Creates dictionary to get block id from name
for block in block_data:
    block_lookup[block_data[block]['name']] = int(block)

#Loads biome json
biome_data = json.load(open("data/biome.json"))

#Generate tree given position
def generate_tree(bx, by, world):
    height = randint(4, 6)

    #Random tree height
    for y in range(height):
        world[bx][by - y] = block_lookup["WoodN"]

    #Generate leaves
    for x in range(randint(3, 5)):
        for y in range(randint(2, 4)):
            world[bx - x // 2][by - y - height] = block_lookup["LeavesN"]
            world[bx + x // 2][by - y - height] = block_lookup["LeavesN"]

    return world

#Generate cactus
def generate_cactus(bx, by, world):
    #Gets random height
    height = randint(2, 4)

    #Changes those blocks to cactus
    for y in range(height):
        world[bx][by - y] = block_lookup["Cactus"]

    return world

#Generate structure (tree or cactus)
def generate_structure(bx, by, world, structure):

    #Gets the structure function based on given string
    structures = {'tree':generate_tree,
                  'cactus':generate_cactus}

    #Returns new world with structures
    return structures[structure](bx, by, world)

# ----- Game World Construction Function
def generate_world(world_seed, biome_min, biome_max, w, h):
    """ Creates a world object randomly generated using a user-inputted seed. """

    while True:

        try:

            # Set the initial seed for the random module (random.seed())
            seed(world_seed)

            # Create a blank map (2D list filled with '0' strings
            world = [[0 for y in range(h)] for x in range(w)]
            # Generates the random values for the terrain construction
            terrain = [randrange(20) + 40 for _ in range(w)]

            #Empty biome map
            biomes = []

            #Generates biomes
            for __ in range(w//biome_min):

                #Biome at cursor
                biome_select = choice(list(biome_data))

                #Biomes size
                for _ in range(randint(biome_min, biome_max)):
                    biomes.append(biome_select)

                #World size met
                if len(biomes) >= w:
                    biomes = biomes[:w] #Truncate selection
                    break


            # ----- Construct the Terrain
            # Counter that changes dynamically to check through all blocks in the terrain list
            cur_pos = 0
            # Runs through all the generated numbers in a while loop
            while cur_pos < w:

                # print(".", end="")

                # Check to see if terrain gap is too large

                if abs(terrain[cur_pos] - terrain[cur_pos - 1]) > biome_data[str(biomes[cur_pos])]["maxh"]:  # if terrain gap is larger than threshhold (too big)

                    for n in range(randint(biome_data[str(str(biomes[cur_pos]))]["minx"], biome_data[str(str(biomes[cur_pos]))]["maxx"])):
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

                        #Top layer
                        if y - terrain[x] == 1:

                            #Sets the layer with block specified in biome config
                            world[x][y] = block_lookup[biome_data[biomes[x]]["layer"]["top"]]

                            if randint(0, 10) == 0 and x + 10 < w:
                                world = generate_structure(x, y - 1, world, choice(biome_data[biomes[x]]["structure"]))

                        #Middle layer
                        elif y - terrain[x] < randint(3, 8):
                            world[x][y] = block_lookup[biome_data[biomes[x]]["layer"]["middle"]]

                        #Base
                        else:
                            world[x][y] = block_lookup[biome_data[biomes[x]]["layer"]["lower"]]

                        #Generate ores
                        # Coal
                        if 10 + terrain[x] > y > 5 + terrain[x] and randint(0, 200) == 0:
                            for cluster in range(randint(3, 10)):
                                world[x + randint(-4, 4)][y + randint(-4, 4)] = block_lookup["Coal Ore"]

                        # Iron
                        if 30 + terrain[x] > y > 20 + terrain[x] and randint(0, 200) == 0:

                            for cluster in range(randint(3, 6)):
                                world[x + randint(-4, 4)][y + randint(-4, 4)] = block_lookup["Iron Ore"]

                        # Gold
                        if 80 > y > 65 and randint(0, 400) == 0:
                            for cluster in range(randint(3, 6)):
                                world[x + randint(-4, 4)][y + randint(-4, 4)] = block_lookup["Gold Ore"]

                        # Diamonds
                        if 80 > y > 70 and randint(0, 500) == 0:
                            for cluster in range(randint(1, 5)):
                                world[x + randint(-3, 3)][y + randint(-3, 3)] = block_lookup["Diamond Ore"]

                        # Bedrock
                        if y > 92 or y > 87 and randint(0, 3) == 0:
                            world[x][y] = block_lookup["Bed Rock"]

            # Last edit, adding extras to the top of the world to prevent problems
            world = [[0] * 40 + x for x in world]

            # Return the world object for use
            return np.array(world)

        except:
            world_seed += '1'
