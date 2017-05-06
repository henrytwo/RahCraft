from pygame import *
import time as t

init()

display.set_caption("Timer Demo!")
screen = display.set_mode((800, 600))

square = Rect(380, 280, 40, 40)

hurt = 0
hurtDict = {0: (0, 255, 0),
            1: (255, 0, 0)}

INVULNERABILITYEVENT = USEREVENT + 1
invulnerabilityTimer = time.set_timer(INVULNERABILITYEVENT, 3000)

while True:
    for e in event.get():
        if e.type == QUIT:
            break

        elif e.type == MOUSEBUTTONDOWN:
            if not hurt:
                print("OW!")

                hurt = 1
                seconds = 1

                sTime = t.time()

                event.clear(INVULNERABILITYEVENT)
                invulnerabilityTimer = time.set_timer(INVULNERABILITYEVENT, 3000)

        elif e.type == INVULNERABILITYEVENT:
            if hurt:
                print(t.time() - sTime)
                print("Free")

            hurt = 0

    else:

        draw.rect(screen, hurtDict[hurt], square)

        display.update()
        continue

    break

display.quit()
exit()
