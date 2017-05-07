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

def text(text, pos):
    text_surface = minecraft_font.render(text, True, (255, 255, 255))
    text_shadow = minecraft_font.render(text, True, (0, 0, 0))
    shadow_surface = Surface((text_surface.get_width(), text_surface.get_height()))
    shadow_surface.blit(text_shadow, (0, 0))
    shadow_surface.set_alpha(100)

    screen.blit(text_shadow, (pos[0] + 2, pos[1] + 2))
    screen.blit(text_surface, pos)
