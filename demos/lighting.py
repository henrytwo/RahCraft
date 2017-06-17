from pygame import *
from random import *

size = (800,800)

screen = display.set_mode(size)

tile_size =10

world = [[randint(0, 16777215) for y in range(size[0]//tile_size)] for x in range(size[1]//tile_size)]

def distance(ax, ay, bx, by):
    return ((ax - bx)**2 + (ay - by)**2)**0.5



tint = Surface((tile_size, tile_size))
tint.fill((0, 0, 0))
tint.set_alpha(99)

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    mx, my = mouse.get_pos()

    light = [[x, 0] for x in range(size[0])]

    light.append((mx - tile_size//2, my - tile_size//2))

    for x in range(len(world)):
        for y in range(len(world[x])):

            for l in light:
                draw.rect(screen, world[x][y], (x * tile_size, y * tile_size, tile_size, tile_size))

                tint.set_alpha(min(distance(*l, x * tile_size, y * tile_size), 255))
                screen.blit(tint, (x * tile_size, y * tile_size))


    display.flip()

quit()

