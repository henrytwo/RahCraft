from pygame import *

init()
screen = display.set_mode((800, 600))
tick = 0
display.update()
running = True
clock = time.Clock()

screen.fill((135, 206, 235))
display.update()
sky_color = [135, 206, 235]

BLUE_VALUE = 235

darken = True

while running:
    for e in event.get():
        if e == QUIT:
            running = False

    if darken:
        sky_color = [i - 1 for i in sky_color]
        screen.fill([max(x, 0) for x in sky_color])

        if sky_color[2] == 30:
            darken = False
    else:
        sky_color = [i + 1 for i in sky_color]
        screen.fill([max(x, 0) for x in sky_color])

        if sky_color[2] == BLUE_VALUE:
            darken = True

    print(sky_color, darken)
    clock.tick(20)
    display.update()

quit()
