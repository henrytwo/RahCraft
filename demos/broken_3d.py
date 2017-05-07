from pygame import *
from random import *
import pickle

world = [[[1 for z in range(4)] for y in range(15)] for x in range(15)]

clock = time.Clock()

block_size = 20
y_offset = 0
x_offset = 5000

display.set_caption("Minecraft Render Test")
screen = display.set_mode((800, 520))

def draw_block(screen,x,y):
    point_list = [(x, y), (x + 20, y + 15), (x, y + 30), (x - 20, y + 15)]
    draw.polygon(screen, (0, 255, 0), point_list, 0)

    point_list = [(x, y + 30), (x - 20, y + 15), (x - 20, y + 35), (x, y + 50)]
    draw.polygon(screen, (135, 32, 22), point_list, 0)

    point_list = [(x, y + 30), (x + 20, y + 15), (x + 20, y + 35), (x, y + 50)]
    draw.polygon(screen, (165, 42, 42), point_list, 0)

    point_list = [(x, y), (x + 20, y + 15), (x, y + 30), (x - 20, y + 15)]
    draw.polygon(screen, (0, 200, 0), point_list, 5)

    point_list = [(x, y + 30), (x - 20, y + 15), (x - 20, y + 35), (x, y + 50)]
    draw.polygon(screen, (115, 22, 12), point_list, 5)

    point_list = [(x, y + 30), (x + 20, y + 15), (x + 20, y + 35), (x, y + 50)]
    draw.polygon(screen, (115, 32, 32), point_list, 5)

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:

        offset_x, offset_y = 200,-100
        for z in range(0,80,20):

            for x in range(0,300,20):
                x += offset_x
                
                for y in range(0,200,15):
                    y += offset_y

                    draw_block(screen,x - y/0.75, (y + 0.75*x) - z)


        clock.tick(120)
        display.update()
        continue

    break

display.quit()
raise SystemExit
