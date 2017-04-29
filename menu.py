import pickle
import socket
from multiprocessing import *
from collections import *
import numpy as np
from pygame import *
from random import *
import os


def center(x,y,canvas_w,canvas_h,object_w,object_h):
    return (x + canvas_w//2 - object_w//2, y + canvas_h//2 - object_h//2)


class Button:
    def __init__(self,x,y,w,h,function,text):
        self.rect = Rect(x,y,w,h)
        self.text = text
        self.function = function

    def trigger(self):
        return self.function

    def highlight(self):
        button_hover = transform.scale(image.load("textures/menu/button_hover.png"), (self.rect.w, self.rect.h))
        screen.blit(button_hover, (self.rect.x, self.rect.y))

    def mouse_down(self):
        button_pressed = transform.scale(image.load("textures/menu/button_pressed.png"), (self.rect.w, self.rect.h))
        screen.blit(button_pressed, (self.rect.x, self.rect.y))

    def idle(self):
        button_idle = transform.scale(image.load("textures/menu/button_idle.png"), (self.rect.w, self.rect.h))
        screen.blit(button_idle, (self.rect.x, self.rect.y))

    def update(self, mx, my, mb, size, unclick):

        minecraft_font = font.Font("fonts/minecraft.ttf", size)

        if self.rect.collidepoint(mx, my):
            if unclick:
                return self.trigger()

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


def menu():

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (400 - logo.get_width() // 2, 100))

    button_list = []

    button_list.append(Button(200, 175, 400, 40, 'game',"Connect to server"))
    button_list.append(Button(200, 225, 400, 40, 'help', "Help"))
    button_list.append(Button(200, 275, 400, 40, 'options', "Options"))
    button_list.append(Button(200, 325, 195, 40, 'about', "About"))
    button_list.append(Button(404, 325, 195, 40, 'exit',"Exit"))

    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True


        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            for button in button_list:
                nav_update = button.update(mx, my, mb, 10, unclick)

                if nav_update != None:
                    return nav_update

            clock.tick(120)
            display.update()

            continue

        break


def game():
    '''
    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (400 - logo.get_width() // 2, 100))

    button_list = []

    button_list.append(Button(200, 175, 400, 40, 'game',"Connect to server"))
    button_list.append(Button(200, 225, 400, 40, 'help', "Help"))
    button_list.append(Button(200, 275, 400, 40, 'options', "Options"))
    button_list.append(Button(200, 325, 195, 40, 'about', "About"))
    button_list.append(Button(404, 325, 195, 40, 'exit',"Exit"))
    '''
    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                exit()
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True


        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            '''
            for button in button_list:
                nav_update = button.update(mx, my, mb, 10, unclick)

                if nav_update != None:
                    return nav_update
            '''

            screen.fill(randint(0,15777216))

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

    while True:
        if navigation == 'menu':
            navigation = menu()
        if navigation == 'game':
            navigation = game()

    display.quit()
    raise SystemExit
