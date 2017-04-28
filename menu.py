import pickle
import socket
from multiprocessing import *
from collections import *
import numpy as np
from pygame import *
import os

class button:
    def __init__(self,w,h,x,y,text):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.text = text

    def update(mx,my):
        if (mx,my).colliderect(Rect(self.x,self.y,self.w,self.h)):
            if click:
                trigger()
            else:
                highlight()

    
        

def menu(screen):
    wallpaper = transform.scale(image.load("textures/gui/menu_wallpaper.png"), (955, 500))
    screen.blit(wallpaper,(0,0))



if __name__ == '__main__':
    clock = time.Clock()

    navigation = 'menu'

    display.set_caption("Random World Generator!")
    screen = display.set_mode((800, 500))


    while True:

        for e in event.get():
            if e.type == QUIT:
                break

        else:

            if navigation == 'menu':
                menu(screen)

            clock.tick(120)
            display.update()

            continue

        break

    display.quit()
    raise SystemExit
