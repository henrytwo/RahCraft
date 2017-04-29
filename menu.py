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
        pass

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

        text_surface = minecraft_font.render(self.text, True, (255, 255, 255))
        text_shadow = minecraft_font.render(self.text, True, (0, 0, 0))
        shadow_surface = Surface((text_surface.get_width(), text_surface.get_height()))
        shadow_surface.blit(text_shadow, (0, 0))
        shadow_surface.set_alpha(100)
        textPos = center(self.rect.x, self.rect.y, self.rect.w, self.rect.h, text_surface.get_width(), text_surface.get_height())
        screen.blit(text_shadow, (textPos[0] + 2, textPos[1] + 2))
        screen.blit(text_surface, textPos)
             

def menu(screen):

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (400 - logo.get_width() // 2, 100))

    connect_button = Button(200, 175, 400, 40, "Connect to server")
    help_button = Button(200, 225, 400, 40, "Help")
    about_button = Button(200, 275, 400, 40, "About")
    menu_button = Button(200, 325, 400, 40, "Options")

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

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            connect_button.update(mx, my, mb, 10, unclick)
            help_button.update(mx, my, mb, 10, unclick)
            about_button.update(mx, my, mb, 10, unclick)
            menu_button.update(mx, my, mb, 10, unclick)

            clock.tick(120)
            display.update()

            continue

        break

    



if __name__ == '__main__':
    clock = time.Clock()

    navigation = 'menu'

    display.set_caption("Nothing here")
    screen = display.set_mode((800, 500))

    font.init()

    if navigation == 'menu':
        menu(screen)

    display.quit()
    raise SystemExit
