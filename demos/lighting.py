# from pygame import *
# from random import *
#
# size = (800,800)
#
# screen = display.set_mode(size)
#
# tile_size =10
#
# world = [[randint(0, 16777215) for y in range(size[0]//tile_size)] for x in range(size[1]//tile_size)]
#
# def distance(ax, ay, bx, by):
#     return ((ax - bx)**2 + (ay - by)**2)**0.5
#
#
#
# tint = Surface((tile_size, tile_size))
# tint.fill((0, 0, 0))
# tint.set_alpha(99)
#
# surf = Surface(size)
# surf.fill((0, 0, 0))
# surf.set_alpha(100)
#
#
# while True:
#     for e in event.get():
#         if e.type == QUIT:
#             break
#
#     mx, my = mouse.get_pos()
#
#     light = [[x, 0] for x in range(size[0])]
#
#     light.append((mx - tile_size//2, my - tile_size//2))
#
#     for x in range(len(world)):
#         for y in range(len(world[x])):
#
#             for l in light:
#                 surf.fill((0, 0, 0))
#                 draw.rect(surf, world[x][y], (x * tile_size, y * tile_size, tile_size, tile_size))
#
#     screen.blit(surf, (0, 0))
#
#     #tint.set_alpha(min(distance(*l, x * tile_size, y * tile_size), 255))
#     #screen.blit(tint, (x * tile_size, y * tile_size))
#
#
#     display.flip()
#
# quit()
#


## <code>
SCREEN_SIZE = (800,600)

light_size = 100

## Setup
from pygame import *
init()
screen = display.set_mode(SCREEN_SIZE)

## A black mask for the screen.
mask = Surface(SCREEN_SIZE).convert_alpha()


while True:
    mx, my = mouse.get_pos()

    light_location = (mx, my)

    mask.fill((0, 0, 0, 255))

    ## An inefficiently-drawn shaded "light"
    radius = 200
    t = 255
    delta = 3
    while radius > 50:
        draw.circle(mask, (0, 0, 0, t), light_location, radius)
        t -= delta
        radius -= delta

    draw.circle(mask,(0,0,0,95),light_location,radius)

    ## A red-tinted "light"
    draw.circle(mask,(192,0,0,128),(300,375),50)

    ## A blue screen with a couple of white squares
    screen.fill((0,0,255))
    draw.rect(screen,(255,255,255),(100,100,100,100))
    draw.rect(screen,(255,255,255),(300,250,100,100))

    ## A sharp-edged white "light"
    draw.circle(mask,(0,0,0,0),(mx, my),50)

    ## Cover the screen with the partly-translucent mask
    screen.blit(mask,(0,0))

    ## Make it so
    display.flip()
    ## </code>

