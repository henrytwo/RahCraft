from pygame import *
from random import *

clock = time.Clock()


def generate_tree(bx, by, world):
    height = randint(4, 6)

    for y in range(height):
        world[bx][by - y] = "2"

    for x in range(randint(3, 5)):
        for y in range(randint(2, 4)):
            world[bx - x // 2][by - y - height] = "1"
            world[bx + x // 2][by - y - height] = "1"

    return world


# ----- Game World Construction Function
def generate_world(world_seed, maxHeight, minX, maxX, w, h):
    """ Creates a world object randomly generated using a user-inputted seed. """

    # Set the initial seed for the random module (random.seed())
    seed(world_seed)

    # Create a blank map (2D list filled with '0' strings (50 x 5000 list))
    world = [["0" for y in range(h)] for x in range(w)]
    # Generates the random values for the terrain construction
    terrain = [randrange(30) + 10 for _ in range(w)]

    # ----- Construct the Terrain
    # Counter that changes dynamically to check through all blocks in the terrain list
    cur_pos = 0
    # Runs through all the generated numbers in a while loop
    while cur_pos < len(terrain):

        # print(".", end="")

        # Check to see if terrain gap is too large

        if abs(terrain[cur_pos] - terrain[cur_pos - 1]) > maxHeight:  # if terrain gap is larger than threshhold (too big)

            for n in range(randint(minX, maxX)):
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

                    if randint(0, 10) == 0 and x + 10 < w:
                        world = generate_tree(x, y - 1, world)

                elif y - terrain[x] < randint(3, 8):
                    world[x][y] = "2"

                else:
                    world[x][y] = "3"

    # Return the world object for use
    return world


# ----- Pre-Gameloop Preparation

# Make the block size and block offset
block_size = 20
y_offset = 0
x_offset = 0

# Generate a new world with the function
world = generate_world(input("Seed:\n"), 1, 3, 10, 10000, 100)


def draw_block(x, y, size, colour, colourIn):
    draw.rect(screen, colour, (x, y, block_size, block_size))
    draw.rect(screen, colourIn, (x, y, block_size, block_size), 1)


# Create the game screen
display.set_caption("Random World Generator!")
screen = display.set_mode((800, 500))

# ----- Gameloop

while True:

    for e in event.get():
        if e.type == QUIT:
            break

        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4:
                block_size += 4

            elif e.button == 5:
                block_size = max(8, block_size-4)



    else:
        display.set_caption("Minecrap Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " X: " + str(x_offset // block_size) + " Y:" + str(y_offset // block_size) + " Size:" + str(block_size))

        keys = key.get_pressed()

        if keys[K_d]:
            x_offset += 80 // block_size
        if keys[K_a]:
            x_offset -= 80 // block_size

        if keys[K_w]:
            y_offset -= 80 // block_size
        if keys[K_s]:
            y_offset += 80 // block_size

        mb = mouse.get_pressed()

        mx, my = mouse.get_pos()

        if mb[0] == 1:
            world[((mx - block_size // 2) + x_offset) // block_size][((my - block_size // 2) + y_offset) // block_size] = " "

        if mb[1] == 1:
            world[((mx - block_size // 2) + x_offset) // block_size][((my - block_size // 2) + y_offset) // block_size] = "2"

        if mb[2] == 1:
            world[((mx - block_size // 2) + x_offset) // block_size][((my - block_size // 2) + y_offset) // block_size] = "3"

        # Clear the screen
        screen.fill((30, 144, 255))

        # Redraw the level onto the screen
        for x in range(0, 800, block_size):  # Render blocks
            for y in range(0, 500, block_size):
                if world[(x + x_offset) // block_size][(y + y_offset) // block_size] == "1":
                    draw_block(x, y, block_size, (0, 150, 0), (0, 100, 0))

                elif world[(x + x_offset) // block_size][(y + y_offset) // block_size] == "2":
                    draw_block(x, y, block_size, (129, 68, 32), (99, 38, 12))

                elif world[(x + x_offset) // block_size][(y + y_offset) // block_size] == "3":
                    draw_block(x, y, block_size, (150, 150, 150), (100, 100, 100))

        clock.tick()
        display.update()
        continue

    break

display.quit()
raise SystemExit
