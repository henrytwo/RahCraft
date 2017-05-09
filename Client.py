from pygame import *
from multiprocessing import *
from player import *
import numpy as np
import socket
import rahma
import menu
import Game
import Connection
import pickle


def login():
    pass


def about():
    pass


def options():
    pass


def assistance():
    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    back_button = menu.Button(200, 370, 400, 40, 'menu', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    about_list = ['HELP',
                  '------------------------------------',
                  'BOIII',
                  'SO YOU WANNA PLAY DIS GAME HUH?',
                  'WELL ITS RLLY EZ ACTUALLY',
                  'LEGIT',
                  'YOU TAKE UR FAT FINGERS',
                  'PRESS DOWN',
                  'ON UR KEYBOARD',
                  'AND UR DONE.',
                  'DO U SEE THAT PERIOD????',
                  'IT MEANS *MIC DROP*',
                  '',
                  'THATS RIGHT',
                  'ANYWAYS, GOD SAVE THE QUEEN',
                  'LONG LIVE THE RAHMISH EMPIRE',
                  '']

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

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (400 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, mb, 15, release)

        if nav_update is not None:
            return nav_update

        clock.tick(120)
        display.update()


def server_picker():
    pass


def custom_server_picker():
    pass


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

    UI = {'login': login,
          'menu': menu_screen,
          'about': about,
          'options': options,
          'assistance': assistance,
          'game': Game.game,
          'server_picker': server_picker,
          'custom_server_picker': custom_server_picker,
          'local_server': Connection.local_server,
          'rahmish_server': Connection.rahmish_server}


    while navigation != 'exit':
        navigation = UI[navigation]()

    display.quit()
    raise SystemExit