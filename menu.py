import pickle
import socket
from multiprocessing import *
from collections import *
import numpy as np
from pygame import *
import os

def center(x,y,canvas_w,canvas_h,object_w,object_h):
    return (x + canvas_w//2 - object_w//2, y + canvas_h//2 - object_h//2)


class Button:
    def __init__(self,x,y,w,h,text):
        self.rect = Rect(x,y,w,h)
        self.text = text


    def trigger(self):
        print("hi")

    def highlight(self):
        button_hover = transform.scale(image.load("textures/menu/button_hover.png"), (self.rect.w, self.rect.h))
        screen.blit(button_hover,(self.rect.x,self.rect.y))
        
    def mouse_down(self):
        button_pressed = transform.scale(image.load("textures/menu/button_pressed.png"), (self.rect.w, self.rect.h))
        screen.blit(button_pressed,(self.rect.x,self.rect.y))

    def idle(self):
        button_idle = transform.scale(image.load("textures/menu/button_idle.png"), (self.rect.w, self.rect.h))
        screen.blit(button_idle,(self.rect.x,self.rect.y))
        
    def update(self,mx,my,mb,size,unclick):

        minecraft_font = font.Font("fonts/minecraft.ttf", size)
        
        if self.rect.collidepoint(mx,my):
            if unclick:
                self.trigger()

            if mb[0] == 1:
                self.mouse_down()
                
            else:
                self.highlight()

        else:
            self.idle()

        text_surface = minecraft_font.render(self.text, True, (255,255,255))
        screen.blit(text_surface, center(self.rect.x, self.rect.y, self.rect.w, self.rect.h, text_surface.get_width(), text_surface.get_height()))
             

def menu(screen,unclick):
    
    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper,(0,0))

    mx,my = mouse.get_pos()
    mb = mouse.get_pressed()

    connect_button = Button(200,180,400,40,"Connect to server")
    help_button = Button(200,230,400,40,"Help")
    menu_button = Button(200,280,400,40,"Options")
    
    connect_button.update(mx,my,mb,10,unclick)
    help_button.update(mx,my,mb,10,unclick)
    menu_button.update(mx,my,mb,10,unclick)



if __name__ == '__main__':
    clock = time.Clock()

    navigation = 'menu'

    display.set_caption("Nothing here")
    screen = display.set_mode((800, 500))

    font.init()

    while True:

        click = False 
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                break
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True


        else:

            if navigation == 'menu':
                menu(screen,unclick)

            clock.tick(120)
            display.update()

            continue

        break

    display.quit()
    raise SystemExit
