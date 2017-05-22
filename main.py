from pygame import *
from multiprocessing import *
import pickle
import numpy as np
import socket
import hashlib
import traceback

from components.player import *
import components.rahma as rah
import components.menu as menu
import Game as Game
import platform


def login():
    global username, password, host, port

    def hash_creds(target):
        return hashlib.sha512(target.encode('utf-8')).hexdigest()

    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    login_button = menu.Button(200, 370, 400, 40, 'menu', 'Login offline (Some features restricted)')

    auth_button = menu.Button(200, 320, 400, 40, 'auth', 'AUTHENTICATE WITH SERVER')

    username, password = '', ''

    field_selected = 'user'

    fields = {'user': [menu.TextBox(size[0] // 4, size[1] // 4, 400, 40, 'Username'), username],
              'pass': [menu.TextBox(size[0] // 4, 7 * size[1] // 16, 400, 40, 'Password'), password]}

    while True:

        click = False
        release = False

        pass_event = None

        for e in event.get():

            pass_event = e

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN:
                if e.key == K_RETURN and username and password:
                    return 'auth'

                if e.key == K_TAB:
                    if field_selected == 'user':
                        field_selected = 'pass'
                    else:
                        field_selected = 'user'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        fields[field_selected][1] = fields[field_selected][0].update(screen, mouse, pass_event)

        for field in fields:
            fields[field][0].draw(screen)

            if fields[field][0].rect.collidepoint(mx, my) and click:
                field_selected = field

        nav_update = login_button.update(screen, mx, my, m_press, 15, release)
        if nav_update and username:
            return nav_update

        nav_update = auth_button.update(screen, mx, my, m_press, 15, release)
        if nav_update and username:
            return nav_update

        username, password = fields['user'][1], hash_creds(fields['pass'][1] + fields['user'][1])

        clock.tick(120)
        display.update()


def player_sender(send_queue, server):
    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    while True:
        message = server.recvfrom(16384)
        message_queue.put(pickle.loads(message[0]))


def authenticate():
    global username, password, online, token

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    connecting_text = rah.text("Waiting for AUTH server...", 30)
    screen.blit(connecting_text,
                rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    display.update()

    host, port = 'rahmish.com', 1111

    send_queue = Queue()
    message_queue = Queue()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _server = (host, port)

    send_queue = Queue()
    message_queue = Queue()

    sender = Process(target=player_sender, args=(send_queue, server))
    receiver = Process(target=receive_message, args=(message_queue, server))

    credentials = [username, password]

    server.sendto(pickle.dumps([0, credentials]), _server)

    sender.start()
    receiver.start()

    while True:

        first_message = message_queue.get()

        if first_message == (400,):

            print("Invalid credentials")

            return 'login'

        elif first_message[0] == 1:
            token = str(first_message[1])
            print("Login successful " + token)

            online = True

            return 'menu'


def about():
    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    back_button = menu.Button(200, 370, 400, 40, 'menu', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    about_list = ['The Zen of Python, by Tim Peters',
                  'Beautiful is better than ugly.',
                  'Explicit is better than implicit.',
                  'Simple is better than complex.',
                  'Complex is better than complicated.',
                  'Flat is better than nested.',
                  'Sparse is better than dense.',
                  'Readability counts.',
                  'Special cases aren\'t special enough to break the rules.',
                  '...',
                  'If the implementation is hard to explain, it\'s a bad idea.',
                  'If the implementation is easy to explain, it may be a good idea.',
                  'Namespaces are one honking great idea -- let\'s do more of those!',
                  '',
                  'Developed by: Henry Tu, Ryan Zhang, Syed Safwaan',
                  'ICS3U 2017',
                  '']

    while True:
        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (400 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def assistance():
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

        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (400 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def options():
    return 'menu'


def server_picker():
    global host, port

    with open('data/servers.rah', 'r') as servers:
        server_list = [server.split(' // ') for server in servers.read().split('\n')]

    for server in server_list:
        server[0] = int(server[0])
        server[3] = int(server[3])

    server_menu = menu.ScrollingMenu(server_list, 0, 0, size[0], size[1] - 80)

    button_list = [
        menu.Button((size[0] * 7) // 9 - 100, size[1] - 60, 200, 40, 'custom_server_picker', 'Direct Connect'),
        menu.Button(size[0] // 2 - 100, size[1] - 60, 200, 40, 'add_server', 'Add Server'),
        menu.Button((size[0] * 2) // 9 - 100, size[1] - 60, 200, 40, 'menu', 'Back')]

    while True:
        wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
        screen.blit(wallpaper, (0, 0))

        release = False

        for e in event.get():

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = server_menu.update(screen, release, mx, my, m_press)

        if nav_update:
            host, port = nav_update[1], nav_update[2]
            return nav_update[0]

        server_bar = Surface((size[0], 80))

        server_bar.fill((200, 200, 200))

        server_bar.set_alpha(90)

        screen.blit(server_bar, (0, size[1] - 80))

        for button in button_list:
            nav_update = button.update(screen, mx, my, m_press, 15, release)

            if nav_update:
                if nav_update == 'add_server' and len(server_list) > 4:
                    print("Too many")

                else:
                    return nav_update

        display.update()


def custom_server_picker():
    global host, port

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    buttons = [[0, 'game', "Connect"],
               [1, 'menu', "Back"]]

    ip_menu = menu.Menu(buttons, 0, size[1] // 2, size[0], size[1] // 2)

    field_selected = 'host'

    fields = {'host': [menu.TextBox(size[0] // 4, size[1] // 4, 400, 40, 'Host'), host],
              'port': [menu.TextBox(size[0] // 4, 7 * size[1] // 16, 400, 40, 'Port'), port]}

    while True:

        release = False

        pass_event = None

        for e in event.get():

            pass_event = e

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN:
                if e.key == K_RETURN and host and port:
                    host, port = fields['host'][1], int(fields['port'][1])
                    return 'game'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = ip_menu.update(screen, release, mx, my, m_press)

        if nav_update:

            if nav_update == 'game' and host and port:
                host, port = fields['host'][1], int(fields['port'][1])
                return nav_update

            else:
                return nav_update

        fields[field_selected][1] = fields[field_selected][0].update(screen, mouse, pass_event)

        for field in fields:
            fields[field][0].draw(screen)

            if fields[field][0].rect.collidepoint(mx, my) and click:
                field_selected = field

        display.update()


def server_adder():
    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    buttons = [[0, 'server_picker', "Add"],
               [1, 'server_picker', "Back"]]

    ip_menu = menu.Menu(buttons, 0, size[1] // 2, size[0], size[1] // 2)

    name, host, port = '', '', None

    field_selected = 'name'

    fields = {'name': [menu.TextBox(size[0] // 4, size[1] // 4, 400, 40, 'Name'), name],
              'host': [menu.TextBox(size[0] // 4, size[1] // 4 + 70, 400, 40, 'Host'), host],
              'port': [menu.TextBox(size[0] // 4, size[1] // 4 + 140, 400, 40, 'Port'), port]}

    while True:

        release = False

        pass_event = None

        for e in event.get():

            pass_event = e

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN:
                if e.key == K_RETURN and host and port:
                    name, host, port = fields['name'][1], fields['host'][1], int(fields['port'][1])

                    with open('data/servers.rah', 'w') as servers:
                        line_count = len(servers.read().split('\n'))

                        print(line_count)

                        servers.write('%i // %s // %s // %i' % (line_count, name, host, port))

                    return 'server_picker'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = ip_menu.update(screen, release, mx, my, m_press)

        if nav_update:

            if nav_update == 'server_picker' and fields['name'][1] and fields['host'][1] and fields['port'][1]:

                name, host, port = fields['name'][1], fields['host'][1], int(fields['port'][1])

                with open('data/servers.rah', 'r+') as servers:

                    line_count = len(servers.read().split('\n'))

                    servers.write('\n%i // %s // %s // %i' % (line_count, name, host, port))

                return 'server_picker'

            else:
                return nav_update

        fields[field_selected][1] = fields[field_selected][0].update(screen, mouse, pass_event)

        for field in fields:
            fields[field][0].draw(screen)

            if fields[field][0].rect.collidepoint(mx, my) and click:
                field_selected = field

        display.update()


def menu_screen():
    global username, online, token

    clock = time.Clock()

    menu_list = [[0, 'server_picker', "Connect to server"],
                 [1, 'assistance', "Help"],
                 [2, 'options', "Options"],
                 [3, 'about', "About"],
                 [4, 'exit', "Exit"]]

    main_menu = menu.Menu(menu_list, 0, 0, size[0], size[1])

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (size[0] // 2 - logo.get_width() // 2, 100))

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    version_text = normal_font.render("Rahcraft 0.0.1 Beta", True, (255, 255, 255))
    screen.blit(version_text, (10, 480))

    about_text = normal_font.render("Copyright (C) Rahmish Empire. All Rahs Reserved!", True, (255, 255, 255))
    screen.blit(about_text, (size[0] - about_text.get_width(), 480))

    user_text = normal_font.render("Logged in as: %s" % username, True, (255, 255, 255))
    screen.blit(user_text, (20, 20))

    if online:
        user_text = normal_font.render("AUTH ID: %s" % token, True, (255, 255, 255))
        screen.blit(user_text, (20, 50))

    while True:

        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return 'login'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = main_menu.update(screen, release, mx, my, m_press)

        if nav_update:
            return nav_update

        display.update()


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5276

    if platform.system() == "Windows":
        mixer.init()
        music_enable = True
    else:
        music_enable = False

    online = False

    username = ''
    token = ''

    navigation = 'login'

    size = (800, 500)
    screen = display.set_mode(size)

    rah.rah(screen)

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
          'game': menu_screen,
          'server_picker': server_picker,
          'custom_server_picker': custom_server_picker,
          'add_server': server_adder,
          'auth': authenticate}

    while navigation != 'exit':
        if navigation == 'game':
            navigation = Game.game(screen, username, token, host, port, size, music_enable)

        else:
            navigation = UI[navigation]()

    display.quit()
    raise SystemExit
