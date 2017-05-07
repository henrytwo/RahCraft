from pygame import *
import oldclient
import time as t

# RAHMISH EMPIRE WILL DIE
def rah(screen):
    screen.fill((255, 255, 255))
    splash = image.load('textures/menu/splash.png')
    screen.blit(splash, oldclient.center(0, 0, 800, 500, splash.get_width(), splash.get_height()))
    display.flip()

    t.sleep(1)

def center(x, y, canvas_w, canvas_h, object_w, object_h):
    return x + canvas_w // 2 - object_w // 2, y + canvas_h // 2 - object_h // 2