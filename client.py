import pickle
import socket
from multiprocessing import *
import numpy as np
from pygame import *
import time as t
import os
from math import *
from random import randint

host = "127.0.0.1"
port = 0


def playerSender(sendQueue, server):
    print('Client running...')

    while True:
        tobesent = sendQueue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receiveMessage(messageQueue, server):
    print('Client is ready for connection!')

    while True:
        msg = server.recvfrom(16384)
        messageQueue.put(pickle.loads(msg[0]))


def draw_block(x, y, x_offset, y_offset, block_size, colour, colourIn, screen):
    draw.rect(screen, colour, (x - x_offset % 20, y - y_offset % 20, block_size, block_size))
    draw.rect(screen, colourIn, (x - x_offset % 20, y - y_offset % 20, block_size, block_size), 1)


def get_neighbours(x, y, world):
    return [world[x + 1, y], world[x - 1, y], world[x, y + 1], world[x, y - 1]]


def center(x, y, canvas_w, canvas_h, object_w, object_h):
    return (x + canvas_w // 2 - object_w // 2, y + canvas_h // 2 - object_h // 2)


class Button:
    def __init__(self, x, y, w, h, function, text):
        self.rect = Rect(x, y, w, h)
        self.text = text
        self.function = function

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
                return self.function

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
        textPos = center(self.rect.x, self.rect.y, self.rect.w, self.rect.h, text_surface.get_width(),
                         text_surface.get_height())
        screen.blit(text_shadow, (textPos[0] + 2, textPos[1] + 2))
        screen.blit(text_surface, textPos)


def menu():
    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    logo = transform.scale(image.load("textures/menu/logo.png"), (301, 51))
    screen.blit(logo, (400 - logo.get_width() // 2, 100))

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    version_text = normal_font.render("Minecrap 0.0.1 Beta", True, (255, 255, 255))
    screen.blit(version_text, (10, 480))

    about_text = normal_font.render("Copyright (C) Rahmish Empire. All Rahs Reserved!", True, (255, 255, 255))
    screen.blit(about_text, (800 - about_text.get_width(), 480))

    global username

    user_text = normal_font.render("Logged in as: %s"%username, True, (255, 255, 255))
    screen.blit(user_text, (20, 20))

    button_list = []

    button_list.append(Button(200, 175, 400, 40, 'server_picker', "Connect to server"))
    button_list.append(Button(200, 225, 400, 40, 'help', "Help"))
    button_list.append(Button(200, 275, 400, 40, 'options', "Options"))
    button_list.append(Button(200, 325, 195, 40, 'about', "About"))
    button_list.append(Button(404, 325, 195, 40, 'exit', "Exit"))

    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True


        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            for button in button_list:
                nav_update = button.update(mx, my, mb, 15, unclick)

                if nav_update != None:
                    return nav_update

            clock.tick(120)
            display.update()

            continue

        break

def rahmish_server():
    global host, port
    host = "159.203.176.100"
    port = 5175
    return 'game'

def local_server():
    global host, port
    host = "127.0.0.1"
    port = 5175
    return 'game'

def custom_server_picker():
    global host, port

    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    with open("config", "r") as config:
        config = config.read().split("\n")
        host = config[0]
        port = int(config[1])

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    IpText = normal_font.render("IP address", True, (255, 255, 255))
    PortText = normal_font.render("Port", True, (255, 255, 255))
    sizeChar = normal_font.render("SHZ", True, (255, 255, 255))

    ipfieldRect = (size[0] // 2 - 150, size[1] // 2 - 100, 300, 40)
    portRect = (size[0] // 2 - 150, size[1] // 2 - 30, 300, 40)

    fields = {"ip": "",
              "port": "",
              "none": ""}

    currentField = "none"
    allowed = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4',
               '5', '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "\\", "'", '(', ')', '*', '+', ',', '-', '.', '/',
               ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'", "'"]

    currentField = "ip"

    button_list = []

    button_list.append(Button(200, 370, 400, 40, 'menu', "Back"))
    button_list.append(Button(200, 320, 400, 40, 'game', "Connect to server"))

    while True:
        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'
            if e.type == KEYDOWN:
                if e.unicode in allowed:
                    fields[currentField] += e.unicode
                elif e.key == K_RETURN:
                    try:
                        if fields["ip"] != "":
                            host = fields["ip"]
                        port = int(fields["port"])
                        return 'game'
                    except:
                        pass

                elif e.key == K_BACKSPACE:
                    try:
                        fields[currentField] = fields[currentField][:-1]
                    except:
                        pass

                if e.key == K_z:
                    host = "159.203.176.100"
                    port = 5175
                    return "game"

                if e.key == K_x:
                    host = "127.0.0.1"
                    port = 5175
                    return "game"

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True

        screen.blit(IpText, (ipfieldRect[0], ipfieldRect[1] - IpText.get_height() - 2))
        screen.blit(PortText, (portRect[0], portRect[1] - PortText.get_height()))
        draw.rect(screen, (0, 0, 0), ipfieldRect)
        draw.rect(screen, (151, 151, 151), ipfieldRect, 2)
        draw.rect(screen, (0, 0, 0), portRect)
        draw.rect(screen, (151, 151, 151), portRect, 2)

        screen.blit(normal_font.render(fields["ip"], True, (255, 255, 255)),
                    (ipfieldRect[0] + 3, ipfieldRect[1] + ipfieldRect[3] // 2 - sizeChar.get_height() // 2))
        screen.blit(normal_font.render(fields["port"], True, (255, 255, 255)),
                    (portRect[0] + 3, portRect[1] + portRect[3] // 2 - sizeChar.get_height() // 2))

        mx, my = mouse.get_pos()
        ml, mm, mr = mouse.get_pressed()
        mb = mouse.get_pressed()

        for button in button_list:
            nav_update = button.update(mx, my, mb, 15, unclick)

            if nav_update != None:
                if nav_update == "game":
                    try:
                        if fields["ip"] != "":
                            host = fields["ip"]
                        port = int(fields["port"])
                    except:
                        pass
                return nav_update

        if Rect(ipfieldRect).collidepoint(mx, my) and ml == 1:
            currentField = "ip"

        elif Rect(portRect).collidepoint(mx, my) and ml == 1:
            currentField = "port"

        elif ml == 1:
            currentField = "none"

        clock.tick(120)

        display.flip()


def server_picker():
    global host,port

    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    version_text = normal_font.render("Click on server to join", True, (255, 255, 255))
    screen.blit(version_text, (200, 155))

    button_list = []

    button_list.append(Button(200, 175, 400, 40, 'local_server', "Start local server"))
    button_list.append(Button(200, 225, 400, 40, 'rahmish_server', "*Official* Rahmish Server"))
    button_list.append(Button(200, 275, 400, 40, 'custom_server_picker', "Custom server"))


    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True


        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            for button in button_list:
                nav_update = button.update(mx, my, mb, 15, unclick)

                if nav_update != None:
                    return nav_update

            clock.tick(120)
            display.update()

            continue

        break


def login():
    global username

    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    UsernameText = normal_font.render("Username", True, (255, 255, 255))

    sizeChar = normal_font.render("SHZ", True, (255, 255, 255))

    usernamefieldRect = (size[0] // 2 - 150, size[1] // 2 - 100, 300, 40)

    fields = {"username": ""}

    currentField = "none"
    allowed = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4',
               '5', '6', '7', '8', '9', '!', '"', '#', '$', '%', '&', "\\", "'", '(', ')', '*', '+', ',', '-', '.', '/',
               ':', ';', '<', '=', '>', '?', '@', '[', ']', '^', '_', '`', '{', '|', '}', '~', "'", "'"]

    currentField = "username"

    button_list = []

    button_list.append(Button(200, 370, 400, 40, 'menu', "Login"))

    while True:
        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'
            if e.type == KEYDOWN:
                if e.unicode in allowed:
                    fields[currentField] += e.unicode
                elif e.key == K_RETURN and fields["username"] != "":
                    username = fields["username"]
                    return "menu"

                elif e.key == K_BACKSPACE:
                    try:
                        fields[currentField] = fields[currentField][:-1]
                    except:
                        pass

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True

        screen.blit(UsernameText, (usernamefieldRect[0], usernamefieldRect[1] - UsernameText.get_height() - 2))
        draw.rect(screen, (0, 0, 0), usernamefieldRect)
        draw.rect(screen, (151, 151, 151), usernamefieldRect, 2)

        screen.blit(normal_font.render(fields["username"], True, (255, 255, 255)),
                    (usernamefieldRect[0] + 3, usernamefieldRect[1] + usernamefieldRect[3] // 2 - sizeChar.get_height() // 2))

        mx, my = mouse.get_pos()
        ml, mm, mr = mouse.get_pressed()
        mb = mouse.get_pressed()

        for button in button_list:
            nav_update = button.update(mx, my, mb, 15, unclick)

            if nav_update == "menu" and fields["username"] != "":
                username = fields["username"]

                return nav_update

        if Rect(usernamefieldRect).collidepoint(mx, my) and ml == 1:
            currentField = "username"

        elif ml == 1:
            currentField = "none"

        clock.tick(120)

        display.flip()

def help():
    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    back_button = Button(200, 370, 400, 40, 'menu', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    about_list = '''HELP
------------------------------------
BOIII
SO YOU WANNA PLAY DIS GAME HUH?
WELL ITS RLLY EZ ACTUALLY
LEGIT
YOU TAKE UR FAT FINGERS
PRESS DOWN
ON UR KEYBOARD
AND UR DONE.
DO U SEE THAT PERIOD????
IT MEANS *MIC DROP*

THATS RIGHT
ANYWAYS, GOD SAVE THE QUEEN
LONG LIVE THE RAHMISH EMPIRE
'''.split('\n')

    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True

        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            for y in range(0, len(about_list)):
                about_text = normal_font.render(about_list[y], True, (255, 255, 255))
                screen.blit(about_text, (400 - about_text.get_width() // 2, 50 + y * 20))

            nav_update = back_button.update(mx, my, mb, 15, unclick)

            if nav_update != None:
                return nav_update

            clock.tick(120)
            display.update()

            continue

        break


def about():
    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    back_button = Button(200, 370, 400, 40, 'menu', "Back")

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    about_list = '''The Zen of Python, by Tim Peters
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
...
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!

Developed by: Henry Tu, Ryan Zhang, Syed Safwaan
ICS3U 2017
                    '''.split('\n')

    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True

        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            for y in range(0, len(about_list)):
                about_text = normal_font.render(about_list[y], True, (255, 255, 255))
                screen.blit(about_text, (400 - about_text.get_width() // 2, 50 + y * 20))

            nav_update = back_button.update(mx, my, mb, 15, unclick)

            if nav_update != None:
                return nav_update

            clock.tick(120)
            display.update()

            continue

        break


def options():
    clock = time.Clock()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    back_button = Button(200, 370, 400, 40, 'menu', "Back")

    while True:

        click = False
        unclick = False

        for e in event.get():
            if e.type == QUIT:
                return 'exit'

            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                click = True

            if e.type == MOUSEBUTTONUP and e.button == 1:
                unclick = True

        else:

            mx, my = mouse.get_pos()
            mb = mouse.get_pressed()

            nav_update = back_button.update(mx, my, mb, 15, unclick)

            if nav_update != None:
                return nav_update

            clock.tick(120)
            display.update()

            continue

        break


def game():

    global host, port, username

    sendQueue = Queue()
    messageQueue = Queue()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    minecraft_font = font.Font("fonts/minecraft.ttf", 30)

    text_surface = minecraft_font.render("Connecting to %s:%i..." % (host, port), True, (255, 255, 255))
    text_shadow = minecraft_font.render("Connecting to %s:%i..." % (host, port), True, (0, 0, 0))
    shadow_surface = Surface((text_surface.get_width(), text_surface.get_height()))
    shadow_surface.blit(text_shadow, (0, 0))
    shadow_surface.set_alpha(100)
    textPos = center(0, 0, 800, 500, text_surface.get_width(),
                     text_surface.get_height())
    screen.blit(text_shadow, (textPos[0] + 2, textPos[1] + 2))
    screen.blit(text_surface, textPos)

    display.flip()

    clock = time.Clock()

    # Code to trigger Syed
    with open('block', 'r') as block_lookup:
        block_list = block_lookup.read().strip().split('\n')

    block_list = [block.split(' // ') for block in block_list]

    for index in range(len(block_list)):
        block_list[index][1] = list(map(int, block_list[index][1].split(', ')))
        block_list[index][2] = list(map(int, block_list[index][2].split(', ')))

    block_size = 20
    y_offset = 10 * block_size
    x_offset = 5000 * block_size
    reach = 5 * block_size

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Client connecting to %s:%i" % (host, port))

    server.sendto(pickle.dumps([0, username, x_offset, y_offset]), (host, port))

    sender = Process(target=playerSender, args=(sendQueue, server))
    sender.start()

    receiver = Process(target=receiveMessage, args=(messageQueue, server))
    receiver.start()

    worldSizeX, worldSizeY, x_offset, y_offset = messageQueue.get()


    world = np.array([[-1 for y in range(worldSizeY)] for x in range(worldSizeX)])

    updated = False

    sendQueue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])
    wmsg = messageQueue.get()

    world[wmsg[1] - 5:wmsg[1] + 45, wmsg[2] - 5:wmsg[2] + 31] = np.array(wmsg[3], copy=True)
    block_Select = 1

    block_highlight = Surface((block_size, block_size))
    block_highlight.fill((255, 255, 0))
    block_highlight.set_alpha(100)

    advanced_graphics = True

    block_texture = [transform.scale(image.load("textures/blocks/"+block_list[block][3]), (20, 20)) for block in range(len(block_list))]
    players = {}

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    highlight_good = Surface((20,20))
    highlight_good .fill((255,255,255))
    highlight_good .set_alpha(50)

    highlight_bad = Surface((20,20))
    highlight_bad.fill((255,0,0))
    highlight_bad.set_alpha(90)

    inventory = [[-1 for y in range(6)] for x in range(7)]

    toolbar = image.load("textures/gui/toolbar/toolbar.png")
    selected = image.load("textures/gui/toolbar/selected.png")

    inventory_slot = 0

    while True:
        moved = False
        for e in event.get():
            if e.type == QUIT:
                sender.terminate()
                receiver.terminate()

                return 'menu'

            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4:
                    inventory_slot = min(7, inventory_slot + 1)

                    block_Select = min(len(block_list) - 1, block_Select + 1)

                elif e.button == 5:
                    inventory_slot = max(0, inventory_slot - 1)

                    block_Select = max(0, block_Select - 1)

            elif e.type == KEYDOWN:
                if e.key == K_t:
                    if advanced_graphics:
                        advanced_graphics = False
                    else:
                        advanced_graphics = True

        else:
            display.set_caption("Minecrap Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " X: " + str(
                x_offset // block_size) + " Y:" + str(y_offset // block_size) + " Size:" + str(
                block_size) + " Block Selected:" + str(block_Select))

            keys = key.get_pressed()

            if keys[K_d] and x_offset // block_size < 9950:
                x_offset += 60 // block_size
                moved = True
            elif keys[K_a] and x_offset // block_size > 0:
                x_offset -= 60 // block_size
                moved = True

            if keys[K_w] and y_offset // block_size > 5:
                y_offset -= 60 // block_size
                moved = True
            elif keys[K_s] and y_offset // block_size < 70:
                y_offset += 60 // block_size
                moved = True

            if moved:
                sendQueue.put([[1, x_offset, y_offset], (host, port)])


            DispingWorld = world[x_offset // block_size:x_offset // block_size + 41,
                           y_offset // block_size:y_offset // block_size + 26]
            updateCost = DispingWorld.flatten()
            updateCost = np.count_nonzero(updateCost == -1)

            if updateCost > 3:
                sendQueue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])

            try:
                wmsg = messageQueue.get_nowait()
                if wmsg[0] == 1:
                    players[wmsg[1]] = (wmsg[2], wmsg[3])

                elif wmsg[0] == 2:
                    world[wmsg[1] - 5:wmsg[1] + 45, wmsg[2] - 5:wmsg[2] + 31] = np.array(wmsg[3], copy=True)
                elif wmsg[0] == 3:
                    world[wmsg[1], wmsg[2]] = 0
                elif wmsg[0] == 4:
                    world[wmsg[1], wmsg[2]] = wmsg[3]
            except:
                pass

            mb = mouse.get_pressed()

            mx, my = mouse.get_pos()

            if mb[0] == 1:
                if world[(mx + x_offset) // block_size, (my + y_offset) // block_size] != 0 and hypot(mx-size[0]//2, my-size[1]//2) <= reach:
                    sendQueue.put([[3, (mx + x_offset) // block_size, (my + y_offset) // block_size], (host, port)])
            if mb[2] == 1:
                if world[(mx + x_offset) // block_size, (my + y_offset) // block_size] == 0 and sum(
                        get_neighbours((mx + x_offset) // block_size, (my + y_offset) // block_size, world)) > 0 and hypot(mx-size[0]//2, my-size[1]//2) <= reach:
                    sendQueue.put([[4, (mx + x_offset) // block_size, (my + y_offset) // block_size, block_Select], (host, port)])

            # print((mx + x_offset) // block_size, (my + y_offset) // block_size)

            sky_list = [(255, 254, 206, 255), (255, 255, 201, 255), (255, 252, 155, 255), (255, 251, 134, 255), (253, 250, 137, 255), (255, 251, 134, 255), (255, 250, 126, 255), (255, 247, 120, 255), (254, 245, 118, 255), (255, 244, 116, 255), (255, 241, 110, 255), (255, 238, 108, 255), (254, 237, 107, 255), (254, 235, 106, 255), (255, 232, 106, 255), (255, 230, 104, 255), (255, 227, 104, 255), (254, 221, 105, 255), (255, 219, 105, 255), (255, 214, 106, 255), (255, 210, 107, 255), (255, 207, 109, 255), (255, 204, 112, 255), (255, 201, 111, 255), (254, 198, 111, 255), (254, 196, 112, 255), (255, 196, 115, 255), (255, 194, 113, 255), (255, 194, 114, 255), (255, 192, 115, 255), (255, 189, 115, 255), (254, 187, 116, 255), (255, 186, 117, 255), (254, 185, 116, 255), (254, 185, 118, 255), (254, 185, 118, 255), (254, 185, 120, 255), (254, 185, 120, 255), (254, 186, 121, 255), (255, 187, 122, 255), (255, 188, 120, 255), (255, 188, 120, 255), (255, 187, 122, 255), (255, 186, 124, 255), (255, 187, 124, 255), (255, 187, 126, 255), (255, 186, 127, 255), (255, 186, 127, 255), (255, 186, 127, 255), (255, 186, 127, 255), (255, 186, 127, 255), (255, 185, 129, 255), (254, 185, 128, 255), (252, 185, 130, 255), (250, 184, 132, 255), (248, 185, 134, 255), (246, 184, 135, 255), (245, 184, 137, 255), (243, 185, 139, 255), (243, 184, 140, 255), (242, 185, 142, 255), (241, 184, 141, 255), (239, 184, 143, 255), (237, 184, 142, 255), (237, 185, 145, 255), (235, 186, 146, 255), (233, 185, 147, 255), (231, 185, 149, 255), (229, 185, 150, 255), (229, 185, 150, 255), (228, 185, 151, 255), (228, 185, 151, 255), (227, 184, 150, 255), (225, 184, 152, 255), (221, 185, 153, 255), (221, 186, 154, 255), (221, 186, 156, 255), (219, 184, 154, 255), (218, 184, 156, 255), (218, 184, 157, 255), (216, 184, 159, 255), (216, 184, 159, 255), (214, 184, 160, 255), (214, 184, 160, 255), (212, 184, 162, 255), (212, 184, 162, 255), (210, 184, 161, 255), (210, 184, 161, 255), (209, 183, 160, 255), (209, 182, 161, 255), (209, 182, 163, 255), (208, 182, 165, 255), (205, 182, 166, 255), (203, 181, 167, 255), (202, 183, 169, 255), (201, 183, 169, 255), (200, 184, 169, 255), (198, 182, 167, 255), (199, 181, 167, 255), (199, 181, 167, 255), (199, 181, 169, 255), (199, 181, 171, 255), (197, 180, 172, 255), (195, 180, 173, 255), (194, 181, 175, 255), (194, 181, 175, 255), (194, 181, 175, 255), (194, 181, 175, 255), (194, 181, 175, 255), (193, 180, 174, 255), (190, 179, 175, 255), (190, 179, 175, 255), (189, 179, 177, 255), (189, 179, 177, 255), (187, 179, 177, 255), (187, 179, 177, 255), (185, 180, 177, 255), (185, 180, 177, 255), (184, 180, 177, 255), (184, 180, 177, 255), (184, 180, 177, 255), (184, 180, 177, 255), (183, 179, 176, 255), (183, 179, 176, 255), (182, 178, 177, 255), (182, 178, 177, 255), (182, 178, 179, 255), (182, 178, 179, 255), (179, 177, 180, 255), (179, 177, 180, 255), (178, 176, 181, 255), (179, 177, 182, 255), (179, 177, 182, 255), (177, 175, 180, 255), (176, 175, 180, 255), (176, 175, 180, 255), (176, 175, 180, 255), (176, 175, 180, 255), (174, 175, 179, 255), (174, 175, 179, 255), (174, 175, 179, 255), (174, 175, 179, 255), (173, 174, 179, 255), (172, 173, 178, 255), (170, 173, 180, 255), (170, 173, 180, 255), (170, 173, 182, 255), (170, 173, 182, 255), (169, 172, 181, 255), (169, 172, 181, 255), (168, 172, 183, 255), (168, 172, 183, 255), (168, 172, 183, 255), (167, 171, 182, 255), (166, 170, 182, 255), (166, 170, 182, 255), (166, 170, 182, 255), (166, 170, 182, 255), (164, 170, 182, 255), (163, 169, 181, 255), (163, 169, 181, 255), (162, 168, 180, 255), (161, 167, 181, 255), (161, 167, 181, 255), (160, 168, 181, 255), (160, 168, 181, 255), (161, 169, 182, 255), (160, 168, 181, 255), (160, 168, 181, 255), (159, 166, 182, 255), (159, 166, 184, 255), (158, 165, 183, 255), (157, 164, 182, 255), (157, 164, 182, 255), (157, 164, 182, 255), (157, 164, 182, 255), (156, 165, 182, 255), (155, 164, 181, 255), (155, 164, 181, 255), (155, 164, 181, 255), (155, 164, 181, 255), (154, 163, 180, 255), (153, 162, 179, 255), (152, 161, 178, 255), (152, 161, 178, 255), (152, 161, 178, 255), (152, 160, 179, 255), (152, 160, 179, 255), (152, 160, 179, 255), (150, 158, 177, 255), (150, 158, 177, 255), (150, 158, 177, 255), (150, 158, 177, 255), (149, 157, 176, 255), (149, 157, 176, 255), (149, 157, 176, 255), (147, 158, 176, 255), (147, 158, 176, 255), (146, 159, 176, 255), (145, 158, 175, 255), (144, 157, 174, 255)]


            for y in range(200):

                draw.line(screen, sky_list[y], (0, y*4), (800, y*4), 4)

            # Clear the screen
            # Redraw the level onto the screen
            for x in range(0, 821, block_size):  # Render blocks
                for y in range(0, 521, block_size):
                    block = world[(x + x_offset) // block_size][(y + y_offset) // block_size]

                    if len(block_list) > block > 0:
                        if not advanced_graphics:
                            draw_block(x, y, x_offset, y_offset, block_size, block_list[block][1], block_list[block][2],
                                       screen)
                        else:
                            screen.blit(block_texture[block], (x - x_offset % 20, y - y_offset % 20))

                    elif block == -1:
                        draw_block(x, y, x_offset, y_offset, block_size, (0, 0, 0), (0, 0, 0), screen)

            if hypot(mx - size[0] // 2, my - size[1] // 2) <= reach:
                screen.blit(highlight_good, ((mx + x_offset) // block_size * block_size - x_offset,
                                             (my + y_offset) // block_size * block_size - y_offset))
            else:
                screen.blit(highlight_bad, ((mx + x_offset) // block_size * block_size - x_offset,
                                             (my + y_offset) // block_size * block_size - y_offset))

            draw.rect(screen, (0, 0, 0), (size[0] // 2 - 10, size[1] // 2 - 10, block_size, block_size))
            draw.circle(screen, (0, 0, 0), (size[0]//2, size[1]//2), reach, 2)

            player_name = normal_font.render(username, True, (255, 255, 255))
            screen.blit(player_name, center(size[0] // 2 - 10, size[1] // 2 - 10, 20, 20,
                                            player_name.get_width(), player_name.get_height()))

            for wmsg in players:

                draw.rect(screen, (0, 0, 0), (players[wmsg][0] - x_offset + size[0] // 2 - 10, players[wmsg][1] - y_offset + size[1] // 2 - 10, block_size, block_size))

                player_name = normal_font.render(wmsg, True, (255, 255, 255))
                screen.blit(player_name, center(players[wmsg][0] - x_offset + size[0] // 2 - 10,
                                                players[wmsg][1] - y_offset + size[1] // 2 - 10, 20, 20,
                                                player_name.get_width(), player_name.get_height()))

            screen.blit(toolbar,(400 - toolbar.get_width()//2,456))

            screen.blit(selected, (400 - toolbar.get_width()//2 + 40 * inventory_slot,456))

            for item in range(0, 352, 40):
                draw.rect(screen,(255,0,0),(400 - toolbar.get_width()//2 + item + 6, 462,32,32))

            clock.tick(120)
            display.update()
            continue

        break


if __name__ == '__main__':

    navigation = 'login'

    display.set_caption("Nothing here")
    size = (800, 500)
    screen = display.set_mode((800, 500))

    screen.fill((255, 255, 255))
    splash = image.load('textures/menu/splash.png')
    screen.blit(splash, center(0, 0, 800, 500, splash.get_width(), splash.get_height()))
    display.flip()

    t.sleep(1)

    font.init()

    while navigation != 'exit':
        if navigation == "login":
            navigation = login()
        elif navigation == 'menu':
            navigation = menu()
        elif navigation == 'about':
            navigation = about()
        elif navigation == 'options':
            navigation = options()
        elif navigation == 'help':
            navigation = help()
        elif navigation == 'game':
            navigation = game()

        elif navigation == 'server_picker':
            navigation = server_picker()
        elif navigation == 'custom_server_picker':
            navigation = custom_server_picker()
        elif navigation == 'local_server':
            navigation = local_server()
        elif navigation == 'rahmish_server':
            navigation = rahmish_server()

    display.quit()
    raise SystemExit
