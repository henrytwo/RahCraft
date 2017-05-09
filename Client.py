from pygame import *
from multiprocessing import *
from player import *
import numpy as np
import socket
import rahma
import menu
import pickle

def menu_screen():
    clock = time.Clock()

    menu_list = [[1, 'server_picker', "Connect to server"],
                 [2, 'assistance', "Help"],
                 [3, 'options', "Options"],
                 [4, 'about', "About"],
                 [5, 'exit', "Exit"]]

    main_menu = menu.Menu(menu_list, 0, 0, size[0], size[1])

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (400 - logo.get_width() // 2, 100))

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    version_text = normal_font.render("Minecrap 0.0.1 Beta", True, (255, 255, 255))
    screen.blit(version_text, (10, 480))

    about_text = normal_font.render("Copyright (C) Rahmish Empire. All Rahs Reserved!", True, (255, 255, 255))
    screen.blit(about_text, (800 - about_text.get_width(), 480))

    '''
    global username

    user_text = normal_font.render("Logged in as: %s" % username, True, (255, 255, 255))
    screen.blit(user_text, (20, 20))

    '''

    while True:

        click = False
        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

        mx, my = mouse.get_pos()
        mb = mouse.get_pressed()

        hover_over_button = False

        nav_update = main_menu.update(screen, release, mx, my, mb)
        if nav_update:
            return nav_update

        '''
        if hover_over_button:
            mouse.set_cursor(*click_cursor_data)

        else:
            mouse.set_cursor(*cursors.tri_left)
        '''

        clock.tick(120)
        display.update()

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5175

    navigation = 'menu'

    size = (800, 500)
    screen = display.set_mode(size)

    # rahma.rah(screen)

    init()
    font.init()

    click_cursor = ["      ..                ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX...             ",
                    "     .XX.XX...          ",
                    "     .XX.XX.XX.         ",
                    "     .XX.XX.XX...       ",
                    "     .XX.XX.XX.XX.      ",
                    "     .XX.XX.XX.XX.      ",
                    "...  .XX.XX.XX.XX.      ",
                    ".XX...XXXXXXXXXXX.      ",
                    ".XXXX.XXXXXXXXXXX.      ",
                    " .XXX.XXXXXXXXXXX.      ",
                    "  .XXXXXXXXXXXXXX.      ",
                    "  .XXXXXXXXXXXXXX.      ",
                    "   .XXXXXXXXXXXXX.      ",
                    "    .XXXXXXXXXXX.       ",
                    "    .XXXXXXXXXXX.       ",
                    "     .XXXXXXXXX.        ",
                    "     .XXXXXXXXX.        ",
                    "     ...........        "]

    click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))
    mouse.set_cursor(*cursors.tri_left)
    """
    UI = {'login': login,
          'menu': menu,
          'about': about,
          'options': options,
          'assistance': assistance,
          'game': game,
          'server_picker': server_picker,
          'custom_server_picker': custom_server_picker,
          'local_server': local_server,
          'rahmish_server': rahmish_server}
    """

    while navigation != 'exit':
        navigation = menu_screen()  # UI[navigation]()

    display.quit()
    raise SystemExit