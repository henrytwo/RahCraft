from pygame import *

init()

display.set_caption("Cursors!")
screen = display.set_mode((250, 250))

cursor = ["       oo       ",
          "       oo       ",
          "       oo       ",
          "       oo       ",
          "       oo       ",
          "        o       ",
          "                ",
          "oooooo     ooooo",
          "ooooo     oooooo",
          "                ",
          "       o        ",
          "       oo       ",
          "       oo       ",
          "       oo       ",
          "       oo       ",
          "       oo       "]

print(len(cursor), len(cursor[0]))

cursorData = ((len(cursor), len(cursor[0])), (len(cursor) // 2, len(cursor[0]) // 2), *cursors.compile(cursor))
mouse.set_cursor(*cursorData)

while True:
    for e in event.get():
        if e.type == QUIT:
            break

    else:
        ##        screen.fill((255, 255, 255))

        display.update()
        continue

    break

display.quit()
exit()
