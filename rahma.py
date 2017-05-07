from pygame import *
import client
import time as t

# RAHMISH EMPIRE WILL DIE
def rah(screen):
    screen.fill((255, 255, 255))
    splash = image.load('textures/menu/splash.png')
    screen.blit(splash, client.center(0, 0, 800, 500, splash.get_width(), splash.get_height()))
    display.flip()

    t.sleep(1)