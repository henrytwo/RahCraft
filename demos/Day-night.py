from pygame import *

init()
screen = display.set_mode((800, 600))
tick = 0
display.update()
running = True
clock = time.Clock()

background_darken = Surface((800, 600))
background_darken.fill((0, 0, 0))
background_darken.set
while running:
    for e in event.get():
        if e == QUIT:
            running = False

    clock.tick(1)
    display.update()

quit()
