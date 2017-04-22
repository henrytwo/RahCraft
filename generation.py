from random import *
from pickle import *

def generate_tree(bx,by,world):

    height = randint(4,6)

        
    for y in range(height):
        world[bx][by-y] = "2"


    for x in range(randint(3,5)):
        for y in range(randint(2,4)):
            world[bx - x//2][by - y - height] = "1"
            world[bx + x//2][by - y - height] = "1"

    return world




# ----- Game World Construction Function
def generate_world(world_seed,maxHeight,minX,maxX,w,h):

    """ Creates a world object randomly generated using a user-inputted seed. """

    # Set the initial seed for the random module (random.seed())
    seed(world_seed)
    
    # Create a blank map (2D list filled with '0' strings (50 x 5000 list))
    world = [["0" for y in range(h)] for x in range(w)]
    # Generates the random values for the terrain construction
    terrain = [randrange(30)+10 for _ in range(w)]



    # ----- Construct the Terrain
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
                    world[x][y] = "1"

                    if randint(0,10) == 0 and x + 10 < w:
                        world = generate_tree(x,y - 1,world)

                elif y - terrain[x] < randint(3,8):
                    world[x][y] = "2"

                else:
                    world[x][y] = "3"


    # Return the world object for use
    return world

# Generate a new world with the function
world = generate_world(input("Seed:\n"),1,3,10,10000,100)

#Dumps world to file
with open('world.pkl', 'wb') as file:
    dump(world, file)

