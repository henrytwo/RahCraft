from pygame import *
import pickle
import socket
import hashlib
import traceback

import components.rahma as rah
import components.menu as menu
import Game as Game
import webbrowser
import json
from random import *
from multiprocessing import *
import urllib.request
import zipfile
import os
import glob
from shutil import copyfile, copy2, rmtree

#https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                copy2(s, d)

def software_update():
    global screen, current_version, current_build, size

    display.set_caption("RahCraft Update Service")

    rah.wallpaper(screen, size)

    title_text = rah.text("Welcome to RahCraft! Let's get you up to date", 20)
    screen.blit(title_text, (size[0] // 2 - title_text.get_width() // 2, size[1] // 4 - title_text.get_height() - 50))

    update = None

    try:
        req = urllib.request.Request('https://rahcraft.github.io/rahcraft.txt', headers={'User-Agent': 'Mozilla/5.0'})

        with urllib.request.urlopen(req) as response:
            extracted_file = str(response.read())[2:][:-3].split('\\n')

        latest_version = int(extracted_file[0])
        latest_build = extracted_file[1]
        update_location = extracted_file[2]

        if current_version < latest_version:

            update_text = rah.text("Good news! RahCraft v%s is now available!" % latest_build, 18)

            draw.rect(screen, (0, 0, 0),
                      (size[0] // 2 - max((update_text.get_width() + 20)//2, size[0]//4 + 20), size[1] // 2 - 90, max(update_text.get_width() + 20, size[0]//2 + 40), 200))

            draw.rect(screen, (150, 150, 150),
                      (size[0] // 2 - max((update_text.get_width() + 20)//2, size[0]//4 + 20), size[1] // 2 - 100, max(update_text.get_width() + 20, size[0]//2 + 40), 200))

            screen.blit(update_text,
                        (size[0] // 2 - update_text.get_width() // 2, size[1] // 2 - update_text.get_height() - 50))

            exit_button = menu.Button(size[0] // 4, size[1] // 2 + 200, size[0] // 2, 40, 'exit', 'Exit game')

            update_button = menu.Button(size[0] // 4, size[1] // 2 - 20, size[0] // 2, 40, 'do_update', 'Update now')
            skip_button = menu.Button(size[0] // 4, size[1] // 2 + 30, size[0] // 2, 40, 'skip_update', 'Skip')

            while True:

                release = False

                for e in event.get():
                    if e.type == QUIT:
                        return 'exit'

                    if e.type == MOUSEBUTTONUP and e.button == 1:
                        release = True

                    if e.type == VIDEORESIZE:
                        screen = display.set_mode((e.w, e.h), RESIZABLE)
                        return 'update'

                mx, my = mouse.get_pos()
                m_press = mouse.get_pressed()

                if skip_button.update(screen, mx, my, m_press, 15, release):
                    update = 'no'

                if update_button.update(screen, mx, my, m_press, 15, release):
                    update = 'yes'

                if exit_button.update(screen, mx, my, m_press, 15, release):
                    return 'exit'

                if update:

                    if update == 'yes':

                        rah.wallpaper(screen, size)

                        update_text = rah.text("Downloading updates", 18)
                        subupdate_text = rah.text("This shouldn't take long...", 18)

                        draw.rect(screen, (0, 0, 0),
                                  (size[0] // 2 - max((update_text.get_width() + 20) // 2, size[0] // 4 + 20),
                                   size[1] // 2 - 90, max(update_text.get_width() + 20, size[0] // 2 + 40), 200))

                        draw.rect(screen, (150, 150, 150),
                                  (size[0] // 2 - max((update_text.get_width() + 20) // 2, size[0] // 4 + 20),
                                   size[1] // 2 - 100, max(update_text.get_width() + 20, size[0] // 2 + 40), 200))

                        screen.blit(update_text,
                                    (size[0] // 2 - update_text.get_width() // 2,
                                     size[1] // 2 - update_text.get_height()))

                        screen.blit(subupdate_text,
                                    (size[0] // 2 - subupdate_text.get_width() // 2,
                                     size[1] // 2 - subupdate_text.get_height() + 30))

                        display.flip()

                        with urllib.request.urlopen(update_location) as update_file, open('update.zip', 'wb') as out_file:
                            out_file.write(update_file.read())

                        with zipfile.ZipFile('update.zip','r') as zip_file:
                            zip_file.extractall('update')

                        os.remove("update.zip")

                        dir_list = glob.glob('update/*/*')

                        for dir in dir_list:
                            file_name = dir.split('/')[-1]

                            user_files_intact = os.path.isfile('user_data/servers.json') and os.path.isfile('user_data/session.json')

                            if (user_files_intact and file_name != 'user_data') or not user_files_intact:
                                if len(file_name.split('.')) == 2:
                                    copyfile(dir, file_name)
                                else:
                                    copytree(dir, file_name)

                        rmtree("update")

                        current_build, current_version = latest_build, latest_version

                        with open('data/ver.rah', 'w') as version_file:
                            version_file.write('%s\n%s'%(current_version, current_build))

                        return ['information','\n\n\nRahCraft has updated successfully\nPlease restart game to apply changes','exit']

                    elif update == 'no':
                        return 'login'

                display.update()

        else:
            return 'login'

    except:
        print(traceback.format_exc())
        return ['information', '\n\n\n\n\nUnable to perform update software','login']


def login():
    display.set_caption("RahCraft Authentication Service")

    global username, password, host, port, token, screen

    def hash_creds(target):
        return hashlib.sha512(target.encode('utf-8')).hexdigest()

    clock = time.Clock()

    rah.wallpaper(screen, size)

    title_text = rah.text('Welcome to RahCraft! Login to continue', 20)
    screen.blit(title_text, (size[0] // 2 - title_text.get_width() // 2, size[1] // 4 - title_text.get_height() - 50))

    try:
        with open('user_data/session.json', 'r') as session_file:

            session = json.load(session_file)

            if session['name'] and session['token']:
                token = session['token']
                username = session['name']

                return 'auth'

    except ValueError:

        with open('user_data/session.json', 'w') as session_file:
            json.dump({"token": "", "name": ""}, session_file, indent=4, sort_keys=True)

    #test = menu.Switch(20, 20, 100, 40, False, 'Test')
    #test1 = menu.Toggle(20, 65, 100, 40, False, 'Test')
    #test2 = menu.Slider(20, 110, 400, 40, False, 'Test')

    username, password = '', ''

    field_selected = 'Username'

    fields = {'Username': [menu.TextBox(size[0] // 4, size[1] // 2 - 100, size[0] // 2, 40, 'Username'), username],
              'Password': [menu.TextBox(size[0] // 4, size[1] // 2 - 30, size[0] // 2, 40, 'Password'), password]}

    exit_button = menu.Button(size[0] // 4, size[1] // 2 + 200, size[0] // 2, 40, 'exit', 'Exit game')

    auth_button = menu.Button(size[0] // 4, size[1] // 2 + 50, size[0] // 2, 40, 'auth', 'Login')
    signup_button = menu.Button(size[0] // 4, size[1] // 2 + 100, size[0] // 2, 40, 'signup','Need an account? Signup here')

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
    connecting_text = rah.text("Authenticating...", 30)
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

                with open('user_data/session.json', 'w') as session_file:
                    json.dump({"token": "%s" % token, "name": "%s" % username}, session_file, indent=4, sort_keys=True)

                online = True
                server.close()
                return 'menu'

            else:
                server.close()

                username = ''
                token = ''

                with open('user_data/session.json', 'w') as session_file:
                    json.dump({"token": "", "name": ""}, session_file, indent=4, sort_keys=True)

                return 'reject'
    except:
        server.close()

        with open('user_data/session.json', 'w') as session_file:
            json.dump({"token": "", "name": ""}, session_file, indent=4, sort_keys=True)

        return "information", '\n\n\n\n\nUnable to connect to authentication servers\nTry again later\n\n\nVisit rahmish.com/status.php for help', "login"


def about():
    global screen

    sound_object = mixer.Sound('sound/music/about.wav')
    sound_object.play(0)

    rah.wallpaper(screen, size)

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    about_list = ['RahCraft',
                  '',
                  '',
                  'The Zen of Python, by Tim Peters',
                  'Beautiful is better than ugly.',
                  'Explicit is better than implicit.',
                  'Simple is better than complex.',
                  'Complex is better than complicated.',
                  'Flat is better than nested.',
                  'Sparse is better than dense.',
                  'Readability counts.',
                  'Special cases aren\'t special enough to break the rules.',
                  'Although practicality beats purity.',
                  'Errors should never pass silently.',
                  'Unless explicitly silenced.',
                  'In the face of ambiguity, refuse the temptation to guess.',
                  'There should be one-- and preferably only one --obvious way to do it.',
                  "Although that way may not be obvious at first unless you're Dutch.",
                  'Now is better than never.',
                  'Although never is often better than *right* now.',
                  'If the implementation is hard to explain, it\'s a bad idea.',
                  'If the implementation is easy to explain, it may be a good idea.',
                  'Namespaces are one honking great idea -- let\'s do more of those!',
                  '',
                  'rahmish.com',
                  '',
                  'RahCraft (C) Rahmish Empire, All Rahs Reserved',
                  '',
                  'Developed by: Henry Tu, Ryan Zhang, Syed Safwaan',
                  'ICS3U 2017',
                  'Vincent Massey Secondary School',
                  '',
                  '',
                  '                 !#########       #                 ',
                  '               !########!          ##!              ',
                  '            !########!               ###            ',
                  '         !##########                  ####          ',
                  '       ######### #####                ######        ',
                  '        !###!      !####!              ######       ',
                  '          !           #####            ######!      ',
                  '                        !####!         #######      ',
                  '                           #####       #######      ',
                  '                             !####!   #######!      ',
                  '                                ####!########       ',
                  '             ##                   ##########        ',
                  '           ,######!          !#############         ',
                  '         ,#### ########################!####!       ',
                  "       ,####'     ##################!'    #####     ",
                  "     ,####'            #######              !####!  ",
                  "    ####'                                      #####",
                  '    ~##                                          ##~']
    scroll_y = size[1]

    keith_meme = transform.scale(image.load('textures/keith.png'), (size))
    keith_surface = Surface(size)
    keith_surface.blit(keith_meme, (0, 0))
    keith_surface.set_alpha(1)

    clock = time.Clock()

    while True:

        if scroll_y < -20 * len(about_list):
            sound_object.stop()
            return 'menu'

        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                sound_object.stop()
                return 'about'

            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    sound_object.stop()
                    return 'menu'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        rah.wallpaper(screen, size)

        screen.blit(keith_surface, (0,0))

        keith_surface.set_alpha(100 * (scroll_y/(-20 * len(about_list))))

        for y in range(0, len(about_list)):
            about_text = normal_font.render(about_list[y], True, (255, 255, 255))
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20 + scroll_y))

        scroll_y -= 1

        display.update()
        clock.tick(30)


def reject():
    global screen

    rah.wallpaper(screen, size)

    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'login', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    auth_list = ['',
                 '',
                 '',
                 'AUTHENTICATION FAILED',
                 '',
                 'Username or Password is invalid',
                 'Ensure capslock is disabled and credentials',
                 'match those provided at time of account creation',
                 '',
                 'If you forget your password, reset it at',
                 'rahmish.com/management.php',
                 '',
                 '',
                 'RahCraft (C) Rahmish Empire, All Rahs Reserved',
                 '',
                 'Developed by: Henry Tu, Ryan Zhang, Syed Safwaan',
                 'ICS3U 2017'
                 ]

    while True:
        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'reject'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(auth_list)):
            about_text = normal_font.render(auth_list[y], True, (255, 255, 255))
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def crash(error, previous):
    global screen

    # rah.wallpaper(screen, size)

    tint = Surface(size)
    tint.fill((0, 0, 255))
    tint.set_alpha(99)

    screen.blit(tint, (0, 0))

    back_button = menu.Button(size[0] // 4, size[1] - 200, size[0] // 2, 40, previous, "Return")

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
                                           '',
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
                return 'crash', error, previous

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(about_list)):
            about_text = rah.text(about_list[y], 15)
            screen.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 10 + y * 20))

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()


def information(message, previous):
    global screen

    rah.wallpaper(screen, size)

    # tint = Surface(size)
    # tint.fill((0, 0, 255))
    # tint.set_alpha(99)

    # screen.blit(tint, (0,0))

    back_button = menu.Button(size[0] // 4, size[1] - 200, size[0] // 2, 40, previous, "Okay")

    message_list = list(map(str, message.split('\n')))

    while True:
        release = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'information', message, previous

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        for y in range(0, len(message_list)):
            about_text = rah.text(message_list[y], 15)
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
    global screen

    rah.wallpaper(screen, size)
    back_button = menu.Button(size[0] // 4, size[1] - 130, size[0] // 2, 40, 'menu', "Back")

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

        nav_update = back_button.update(screen, mx, my, m_press, 15, release)

        if nav_update is not None:
            return nav_update

        display.update()

def receive_message(message_queue, server):
    rah.rahprint('Ready to receive command...')

    while True:
        msg = server.recvfrom(163840)
        message_queue.put(pickle.loads(msg[0]))

def status_screen(status, size, screen):

    rah.wallpaper(screen, size)

    connecting_text = rah.text("Updating servers...", 30)
    screen.blit(connecting_text,
              rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    status_text = rah.text(status, 15)
    screen.blit(status_text, rah.center(0, 50, size[0], size[1], status_text.get_width(), status_text.get_height()))

    display.flip()
def server_picker():

    global screen, host, port

    status_screen('Indexing servers', size, screen)

    with open('user_data/servers.json', 'r') as servers:
        server_dict = json.load(servers)

    server_list = []

    for server in server_dict:
        server_list.append([int(server), server_dict[server]['name'], server_dict[server]['host'], server_dict[server]['port'], '', 501])

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_queue = Queue()

    receiver = Process(target=receive_message, args=(message_queue, server))
    receiver.start()

    status_screen('Pinging servers', size, screen)

    for server_info in server_list:
        try:
            SERVERADDRESS = (server_info[2], int(server_info[3]))
            server.sendto(pickle.dumps([102,]), SERVERADDRESS)

        except:
            pass

    rah.wallpaper(screen, size)

    connecting_text = rah.text("Updating servers...", 30)
    screen.blit(connecting_text,
              rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    clock = time.Clock()

    draw.rect(screen, (0, 0, 0), (size[0] // 4, size[1] // 2 + 50, size[0] // 2, 10))

    for check_cycle in range(500):

        draw.rect(screen, (0, 255, 0), (size[0]//4, size[1]//2 + 50, (size[0]//2) * (check_cycle/500), 10))
        display.flip()

        try:
            message = message_queue.get_nowait()

            if message[0] == 102:
                for server_info in server_list:
                    if server_info[2:4] == list(message[2:4]):
                        server_info[4] = message[1]
                        server_info[5] = check_cycle

        except:
            pass

        clock.tick(500)

    receiver.terminate()

    server_menu = menu.ScrollingMenu(server_list, 0, 0, size[0])

    button_list = [
        menu.Button((size[0] * 7) // 9 - size[0] // 8, size[1] - 60, size[0] // 4, 40, 'custom_server_picker',
                    'Direct Connect'),
        menu.Button(size[0] // 2 - size[0] // 8, size[1] - 60, size[0] // 4, 40, 'add_server', 'Add Server'),
        menu.Button((size[0] * 2) // 9 - size[0] // 8, size[1] - 60, size[0] // 4, 40, 'menu', 'Back')]

    y_offset = 50
    percent_visible = 0

    while True:

        rah.wallpaper(screen, size)

        release = False
        right_release = False

        for e in event.get():

            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    release = True
                elif e.button == 3:
                    right_release = True

            if e.type == VIDEORESIZE:
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'server_picker'

            if e.type == MOUSEBUTTONDOWN:

                if e.button == 4:

                    y_offset += 40

                elif e.button == 5:

                    y_offset -= 40

            if e.type == KEYDOWN:
                if e.key == K_r:
                    return 'server_picker'


        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        # Scrolling menu----------------------------------------------------

        page_h = size[1] - 80

        button_h = 75

        if (button_h * len(server_list)) > page_h:
            if y_offset < -button_h * (len(server_list) + 1 - page_h // button_h):
                y_offset = -button_h * (len(server_list) + 1 - page_h // button_h)
            elif y_offset > 50:
                y_offset = 50
        else:
            y_offset = 50

        scroll_pos = int((y_offset / (-button_h * len(server_list))) * page_h)
        percent_visible = page_h / (len(server_list) * button_h)

        bar_rect = Rect(size[0] - 20, 0, 20, page_h)

        draw.rect(screen, (100, 100, 100), bar_rect)
        draw.rect(screen, (230, 230, 230), (size[0] - 18, scroll_pos, 14, (percent_visible * page_h)))

        if bar_rect.collidepoint(mx, my) and m_press[0] == 1:
            y_offset = int((my - (percent_visible * page_h) // 2) / page_h * -button_h * len(server_list))

        # ---------------------------------------------------------------------

        nav_update = server_menu.update(screen, release, right_release, mx, my, m_press, y_offset, size)

        if nav_update:
            if nav_update[0] == 'remove':

                server_update = json.load(open('user_data/servers.json'))

                for server in server_update:
                    if server_update[server]['name'] == nav_update[1] and server_update[server]['host'] == nav_update[
                        2] and server_update[server]['port'] == nav_update[3]:
                        destroy_index = server
                        break

                del server_update[destroy_index]

                with open('user_data/servers.json', 'w') as servers:
                    json.dump(server_update, servers, indent=4, sort_keys=True)

                return 'server_picker'

            elif nav_update[0] == 'remove fail':
                return 'information', "\n\n\n\n\nCouldn't delete server shortcut\nPermission denied", 'server_picker'

            else:
                print(nav_update)
                host, port = nav_update[1], nav_update[2]
                return nav_update[0]

        server_bar = Surface((size[0], 80))
        server_bar.fill((200, 200, 200))
        server_bar.set_alpha(90)
        screen.blit(server_bar, (0, size[1] - 80))

        for button in button_list:
            nav_update = button.update(screen, mx, my, m_press, 15, release)

            if nav_update:
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
                    host, port = fields['Host'][1], int(fields['Port'][1])
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
                host, port = fields['Host'][1], int(fields['Port'][1])
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
                if e.key == K_RETURN and fields['Name'][1] and fields['Host'][1] and fields['Port'][1]:

                    if not fields['Port'][1].isdigit():
                        return 'information', "\n\n\n\n\nCouldn't add server\nInvalid entry for port", 'add_server'

                    server_update = json.load(open('user_data/servers.json'))

                    for server in server_update:
                        if server_update[server]['name'] == fields['Name'][1]:
                            return 'information', "\n\n\n\n\nCouldn't add server\nName conflicts with previous entry", 'add_server'

                    name, host, port = fields['Name'][1], fields['Host'][1], int(fields['Port'][1])

                    server_update.update({str(len(server_update)): {"name": name, "host": host, "port": port}})

                    with open('user_data/servers.json', 'w') as servers:
                        json.dump(server_update, servers, indent=4, sort_keys=True)

                    return 'server_picker'

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

                if not fields['Port'][1].is_digit():
                    return 'information', "\n\n\n\n\nCouldn't add server\nInvalid entry for port", 'add_server'

                server_update = json.load(open('user_data/servers.json'))

                for server in server_update:
                    if server_update[server]['name'] == fields['Name'][1]:
                        return 'information', "\n\n\n\n\nCouldn't add server\nName conflicts with previous entry", 'add_server'

                name, host, port = fields['Name'][1], fields['Host'][1], int(fields['Port'][1])

                server_update.update({str(len(server_update)): {"name": name, "host": host, "port": port}})

                with open('user_data/servers.json', 'w') as servers:
                    json.dump(server_update, servers, indent=4, sort_keys=True)

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
    global current_version

    def draw_screen():
        rah.wallpaper(screen, size)

        with open('data/splashes.txt') as splashes:
            motd = choice(splashes.read().strip().split('\n'))

        logo = transform.scale(image.load("textures/menu/logo.png"), (size[0] // 3, int(size[0] // 3 * 51 / 301)))
        screen.blit(logo, (size[0] // 2 - logo.get_width() // 2, size[1] // 2 - 120 - logo.get_height()))

        minecraft_font = font.Font("fonts/minecraft.ttf", 20)
        text_surface = minecraft_font.render(motd, True, (255, 255, 0))
        text_shadow = minecraft_font.render(motd, True, (0, 0, 0))

        shadow_surface = Surface((text_surface.get_width(), text_surface.get_height()))
        shadow_surface.blit(text_shadow, (0, 0))
        shadow_surface.set_alpha(100)

        text_surface_final = Surface((text_surface.get_width() + 4, text_surface.get_height() + 4), SRCALPHA)

        text_surface_final.blit(text_shadow, (2, 2))
        text_surface_final.blit(text_surface, (0, 0))

        text_surface_final = transform.rotate(text_surface_final, 10)

        screen.blit(text_surface_final, (size[0] // 2 - text_surface_final.get_width() // 2 + 100, size[1] // 2 - 170))

        normal_font = font.Font("fonts/minecraft.ttf", 14)

        version_text = normal_font.render("RahCraft v%s"%current_build, True, (255, 255, 255))
        screen.blit(version_text, (10, size[1] - 20))

        about_text = normal_font.render("Copyright (C) Rahmish Empire. All Rahs Reserved!", True, (255, 255, 255))
        screen.blit(about_text, (size[0] - about_text.get_width(), size[1] - 20))

        user_text = normal_font.render("Logged in as: %s" % username, True, (255, 255, 255))
        screen.blit(user_text, (20, 20))

        if online:
            user_text = normal_font.render("AUTH ID: %s" % token, True, (255, 255, 255))
            screen.blit(user_text, (20, 50))

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

    draw_screen()

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
                screen = display.set_mode((e.w, e.h), RESIZABLE)
                return 'menu'

        mx, my = mouse.get_pos()
        m_press = mouse.get_pressed()

        nav_update = main_menu.update(screen, release, mx, my, m_press)

        if nav_update:
            if nav_update == 'logout':
                username = ''
                token = ''

                with open('user_data/session.json', 'w') as session_file:
                    session_file.write('')

                return 'login'


            else:
                return nav_update

        display.update()


if __name__ == "__main__":
    size = (960, 540)
    screen = display.set_mode(size, DOUBLEBUF + RESIZABLE)

    display.set_caption("RahCraft")
    display.set_icon(transform.scale(image.load('textures/gui/icon.png'), (32, 32)))

    rah.rah(screen)

    with open('data/ver.rah') as version_file:
        version_components = version_file.read().strip().split('\n')

    current_version, current_build = int(version_components[0]), version_components[1]

    host = "127.0.0.1"
    port = 5276

    if True:  # platform.system() == "Windows":
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        music_enable = True
    else:
        music_enable = False

    online = False

    username = ''
    token = ''

    navigation = 'update'

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
          'information': information,
          'auth': authenticate,
          'reject': reject,
          'update':software_update
          }

    while navigation != 'exit':
        size = (screen.get_width(), screen.get_height())

        try:

            if navigation == 'game':
                game_nav = Game.game(screen, username, token, host, port, size, music_enable)

                navigation = game_nav

            elif navigation[0] == 'crash':
                navigation = crash(navigation[1], navigation[2])

            elif navigation[0] == 'information':
                navigation = information(navigation[1], navigation[2])

            else:
                navigation = UI[navigation]()

        except:
            navigation = 'menu'
            crash(traceback.format_exc(), 'menu')



    display.quit()
    raise SystemExit
