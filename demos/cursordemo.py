from pygame import *
from random import *

init()

display.set_caption("Cursors!")
screen = display.set_mode((250, 250))

# cursor = ["       o        ",
#           "       oo       ",
#           "       oo       ",
#           "       oo       ",
#           "       oo       ",
#           "        o       ",
#           "                ",
#           " ooooo     ooooo",
#           "ooooo     ooooo ",
#           "                ",
#           "       o        ",
#           "       oo       ",
#           "       oo       ",
#           "       oo       ",
#           "       oo       ",
#           "        o       "]

cursor = ["      XX                ",
          "     X..X               ",
          "     X..X               ",
          "     X..X               ",
          "     X..X               ",
          "     X..X               ",
          "     X..XXX             ",
          "     X..X..XXX          ",
          "     X..X..X..X         ",
          "     X..X..X..XXX       ",
          "     X..X..X..X..X      ",
          "     X..X..X..X..X      ",
          "XXX  X..X..X..X..X      ",
          "X..XXX...........X      ",
          "X....X...........X      ",
          " X...X...........X      ",
          "  X..............X      ",
          "  X..............X      ",
          "   X.............X      ",
          "    X...........X       ",
          "    X...........X       ",
          "     X.........X        ",
          "     X.........X        ",
          "     XXXXXXXXXXX        "]

cursorData = ((24, 24), (7, 1), *cursors.compile(cursor))
mouse.set_cursor(*cursorData)

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:

        screen.fill((randrange(256), randrange(256), randrange(256)))

        display.update()
        continue

    break

display.quit()
exit()
