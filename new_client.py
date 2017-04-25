from pygame import *
from random import *
import pickle

with open('world.pkl', 'rb') as f:
    world = pickle.load(f)

clock = time.Clock()

block_size = 20
y_offset = 0
x_offset = 5000

display.set_caption("SquareRoot")
screen = display.set_mode((800, 500))

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:
        clock.tick(120)
        display.update()
        continue

    break

display.quit()
raise SystemExit
