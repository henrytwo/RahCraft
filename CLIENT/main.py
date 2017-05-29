from pygame import *
import pickle
import socket
import hashlib
import traceback

import components.rahma as rah
import components.menu as menu
import Game as Game
import webbrowser


def login():
    display.set_caption("RahCraft Authentication Service")
    
    global username, password, host, port, token, screen

    def hash_creds(target):
        return hashlib.sha512(target.encode('utf-8')).hexdigest()

    clock = time.Clock()

    rah.wallpaper(screen, size)

    title_text = rah.text('Welcome to RahCraft! Login to continue', 20)
    screen.blit(title_text, (size[0] // 2 - title_text.get_width() // 2, size[1] // 4 - title_text.get_height() - 30))

    with open('data/session.rah', 'r') as session_file:
        session = session_file.read().strip().split()

        if session:
            token = session[0]
            username = session[1]

            return 'auth'

    username, password = '', ''

    field_selected = 'Username'

    fields = {'Username': [menu.TextBox(size[0] // 4, size[1] // 2 - 100, size[0] // 2, 40, 'Username'), username],
              'Password': [menu.TextBox(size[0] // 4, size[1] // 2 - 30, size[0] // 2, 40, 'Password'), password]}

    exit_button = menu.Button(size[0] // 4, size[1] // 2 + 200, size[0] // 2, 40, 'exit', 'Exit game')

    auth_button = menu.Button(size[0] // 4, size[1] // 2 + 50, size[0] // 2, 40, 'auth', 'Login')
    signup_button = menu.Button(size[0] // 4, size[1] // 2 + 100, size[0] // 2, 40, 'signup',
                                'Need an account? Signup here')

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
                if key.get_mods() & KMOD_CTRL and key.get_mods() & KMOD_SHIFT:
                    if e.key == K_RETURN and username:
                        return 'menu'

                elif e.key == K_RETURN and username and password:
                    return 'auth'

                if e.key == K_TAB:
                    if field_selected == 'Username':
                        field_selected = 'Password'
                    else:
                        field_selected = 'Username'

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'login'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        fields[field_selected][1] = fields[field_selected][0].update(pass_event)

        for field in fields:
            fields[field][0].draw(screen, field_selected)

            if fields[field][0].rect.collidepoint(mx, my) and click:
                field_selected = field

        if signup_button.update(screen, mx, my, m_press, 15, release):
            webbrowser.open('http://rahmish.com/join.php')

        nav_update = auth_button.update(screen, mx, my, m_press, 15, release)
        if nav_update and username:
            return nav_update

        nav_update = exit_button.update(screen, mx, my, m_press, 15, release)
        if nav_update:
            return nav_update

        username, password = fields['Username'][1], hash_creds(
            hash_creds(fields['Password'][1]) + hash_creds(fields['Username'][1]))

        clock.tick(120)
        display.update()


def authenticate():
    global username, password, online, token

    rah.wallpaper(screen, size)
    connecting_text = rah.text("Waiting for AUTH server...", 30)
    screen.blit(connecting_text,
                rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    display.update()

    host, port = 'rahmish.com', 1111

    socket.setdefaulttimeout(10)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVERADDRESS = (host, port)
    socket.setdefaulttimeout(None)

    try:
        server.connect(SERVERADDRESS)

        if token:
            server.send(pickle.dumps([1, [username, token]]))
        else:
            credentials = [username, password]
            server.send(pickle.dumps([0, credentials]))

        while True:

            first_message = pickle.loads(server.recv(4096))

            if first_message[0] == 1:

                if token:
                    token = first_message[1][1]
                    username = first_message[1][0]

                else:
                    token = str(first_message[1])

                with open('data/session.rah', 'w') as session_file:
                    session_file.write('%s\n%s' % (token, username))

                online = True
                server.close()
                return 'menu'

            else:
                server.close()

                username = ''
                token = ''

                with open('data/session.rah', 'w') as session_file:
                    session_file.write('')

                return 'login'
    except:
        server.close()

        with open('data/session.rah', 'w') as session_file:
            session_file.write('')

        return "crash", 'Unable to connect to authentication servers\nTry again later\n', "login"


def about():

    global screen

    rah.wallpaper(screen, size)

    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'menu', "Back")

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

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'about'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def crash(error, previous):
    # wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (wpw, wph))
    # screen.blit(wallpaper, (0, 0))

    screen.fill((0, 0, 255))

    back_button = menu.Button(size[0] // 4, size[1] - 50, size[0] // 2, 40, previous, "Return")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    error_message = list(map(str, error.split('\n')))

    about_list = ['',
                  '',
                  ':( Whoops, something went wrong',
                  '', ] + error_message + ['RahCraft (C) Rahmish Empire, All Rahs Reserved',
                                           '',
                                           'Note: If clicking the button below doesnt',
                                           'do anything, the game is beyond broken',
                                           'and needs to be restarted',
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
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 10 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def assistance():
    global screen

    rah.wallpaper(screen, size)
    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'menu', "Back")

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

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'assistance'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def options():
    return 'menu'


def server_picker():
    global host, port, screen

    with open('data/servers.rah', 'r') as servers:
        server_list = [server.split(' // ') for server in servers.read().split('\n')]

    for server in server_list:
        server[0] = int(server[0])
        server[3] = int(server[3])

    server_menu = menu.ScrollingMenu(server_list, 0, 0, size[0], size[1] - 80)

    button_list = [
        menu.Button((size[0] * 7) // 9 - 100, size[1] - 60, size[0] // 4, 40, 'custom_server_picker', 'Direct Connect'),
        menu.Button(size[0] // 2 - 100, size[1] - 60, size[0] // 4, 40, 'add_server', 'Add Server'),
        menu.Button((size[0] * 2) // 9 - 100, size[1] - 60, size[0] // 4, 40, 'menu', 'Back')]

    while True:

        rah.wallpaper(screen, size)

        release = False

        for e in event.get():

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'server_picker'

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
                    rah.rahprint("Too many")

                else:
                    return nav_update

        display.update()


def custom_server_picker():
    global host, port, screen

    rah.wallpaper(screen, size)

    buttons = [[0, 'game', "Connect"],
               [0, 'server_picker', "Back"]]

    ip_menu = menu.Menu(buttons, 0, size[1] // 2, size[0], size[1] // 2)

    field_selected = 'Host'

    field_list = ['Port', 'Host']


    fields = {'Host': [menu.TextBox(size[0] // 4, size[1] // 4, size[0] // 2, 40, 'Host'), host],
              'Port': [menu.TextBox(size[0] // 4, size[1] // 4 + 80, size[0] // 2, 40, 'Port'), port]}

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

                if e.key == K_TAB:
                    field_list.insert(0, field_list[-1])
                    del field_list[-1]
                    field_selected = field_list[0]

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'custom_server_adder'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = ip_menu.update(screen, release, mx, my, m_press)

        if nav_update:

            if nav_update == 'game' and host and port:
                host, port = fields['host'][1], int(fields['port'][1])
                return nav_update

            else:
                return nav_update

        fields[field_selected][1] = fields[field_selected][0].update(pass_event)

        for field in fields:
            fields[field][0].draw(screen, field_selected)

            if fields[field][0].rect.collidepoint(mx, my) and release:
                field_selected = field

        display.update()


def server_adder():

    global screen

    clock = time.Clock()

    rah.wallpaper(screen, size)

    buttons = [[0, 'server_picker', "Add"],
               [0, 'server_picker', "Back"]]

    ip_menu = menu.Menu(buttons, 0, size[1] // 2, size[0], size[1] // 2)

    name, host, port = '', '', None

    field_list = ['Name', 'Port', 'Host']

    field_selected = 'Name'

    fields = {'Name': [menu.TextBox(size[0] // 4, size[1] // 4, size[0] // 2, 40, 'Name'), name],
              'Host': [menu.TextBox(size[0] // 4, size[1] // 4 + 70, size[0] // 2, 40, 'Host'), host],
              'Port': [menu.TextBox(size[0] // 4, size[1] // 4 + 140, size[0] // 2, 40, 'Port'), port]}

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

                        rah.rahprint(line_count)

                        servers.write('%i // %s // %s // %i' % (line_count, name, host, port))

                if e.key == K_TAB:
                    field_list.insert(0, field_list[-1])
                    del field_list[-1]
                    field_selected = field_list[0]

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'add_server'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = ip_menu.update(screen, release, mx, my, m_press)

        if nav_update:

            if nav_update == 'server_picker' and fields['Name'][1] and fields['Host'][1] and fields['Port'][1]:

                name, host, port = fields['Name'][1], fields['Host'][1], int(fields['Port'][1])

                with open('data/servers.rah', 'r+') as servers:

                    line_count = len(servers.read().split('\n'))

                    servers.write('\n%i // %s // %s // %i' % (line_count, name, host, port))

                return 'server_picker'

            else:
                return nav_update

        fields[field_selected][1] = fields[field_selected][0].update(pass_event)

        for field in fields:
            fields[field][0].draw(screen, field_selected)

            if fields[field][0].rect.collidepoint(mx, my) and release:
                field_selected = field

        display.update()


def menu_screen():
    display.set_caption("RahCraft")
    
    global username, online, token, screen

    clock = time.Clock()

    menu_list = [[0, 'server_picker', "Connect to server"],
                 [1, 'options', "Options"],
                 [2, 'about', "About"],
                 [2, 'assistance', "Help"],
                 [3, 'exit', "Exit"],
                 [4, 'logout', "Logout"]]

    main_menu = menu.Menu(menu_list, 0, 0, size[0], size[1])

    rah.wallpaper(screen, size)

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (size[0] // 2 - logo.get_width() // 2, 100))

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    version_text = normal_font.render("RahCraft 0.0.1 Beta", True, (255, 255, 255))
    screen.blit(version_text, (10, size[1] - 20))

    about_text = normal_font.render("Copyright (C) Rahmish Empire. All Rahs Reserved!", True, (255, 255, 255))
    screen.blit(about_text, (size[0] - about_text.get_width(), size[1] - 20))

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

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h),RESIZABLE)
                return 'menu'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = main_menu.update(screen, release, mx, my, m_press)

        if nav_update:
            if nav_update == 'logout':
                username = ''
                token = ''

                with open('data/session.rah', 'w') as session_file:
                    session_file.write('')

                return 'login'

            else:
                return nav_update

        display.update()


if __name__ == "__main__":
    size = (800, 800)
    screen = display.set_mode(size, DOUBLEBUF + RESIZABLE)

    display.set_caption("RahCraft")
    display.set_icon(transform.scale(image.load('textures/gui/icon.png'),(32,32)))

    rah.rah(screen)

    host = "127.0.0.1"
    port = 5276

    if True:  # platform.system() == "Windows":
        mixer.init()
        music_enable = True
    else:
        music_enable = False

    online = False

    username = ''
    token = ''

    navigation = 'login'

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
          'auth': authenticate
          }

    while navigation != 'exit':
        size = (screen.get_width(), screen.get_height())
        try:

            if navigation == 'game':
                game_nav = Game.game(screen, username, token, host, port, size, music_enable)

                navigation = game_nav

            elif navigation[0] == 'crash':
                navigation = crash(navigation[1], navigation[2])

            else:
                navigation = UI[navigation]()

        except:
            crash(traceback.format_exc(), 'menu')

    display.quit()
    raise SystemExit
