# from pygame import *
# from multiprocessing import *
#
# from subprocess import Popen, PIPE
# from shlex import split
# import platform
# import numpy as np
#
# import socket
# import pickle
# import CLIENT.components.rahma as rah
# from math import *
# import CLIENT.components.player as player
# import CLIENT.components.menu as menu
# import time as ti
# import glob
# import traceback
# import sys
# import os
# import json
# from random import *

import os
import sys

import traceback
import platform
from subprocess import Popen, PIPE
from shlex import split
import glob

import socket
from multiprocessing import *

import pickle
import json

import numpy as np
from math import *

import time as ti
from pygame import *
from random import *

import CLIENT.components.rahma as rah
import CLIENT.components.player as player
import CLIENT.components.menu as menu

def player_sender(send_queue, server):
    rah.rahprint('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    rah.rahprint('Ready to receive command...')

    while True:
        msg = server.recvfrom(163840)
        message_queue.put(pickle.loads(msg[0]))


def load_blocks(block_file, block_size):
    blocks = {}

    block_data = json.load(open("data/" + block_file))

    for block in block_data:
        blocks[int(block)] = {'name': block_data[block]['name'],
                              'texture':transform.scale(image.load("textures/blocks/" + block_data[block]['texture']).convert_alpha(), (block_size, block_size)),
                              'hardness':block_data[block]['hardness'],
                              'sound':block_data[block]['sound'],
                              'collision':block_data[block]['collision'],
                              'icon': transform.scale(image.load("textures/icons/" + block_data[block]['icon']).convert_alpha(), (32, 32)),
                              'tool':block_data[block]['tool'],
                              'drop':block_data[block]['drop'],
                              'tool-required': True if block_data[block]['tool-required'] == 1 else False,
                              'maxstack':block_data[block]['maxstack']}

    return blocks


def load_tools(tool_file):
    tools = {}

    tool_data = json.load(open("data/" + tool_file))

    for tool in tool_data:
        tools[int(tool)] = {'name': tool_data[tool]['name'],
                            'icon': transform.scale(image.load("textures/items/" + tool_data[tool]['icon']).convert_alpha(), (32, 32)),
                            'bonus': tool_data[tool]['bonus'],
                            'speed': tool_data[tool]['speed'],
                            'type': tool_data[tool]['type'],
                            'durability': tool_data[tool]['durability'],
                            'maxstack': 1}

    return tools


def load_items(item_file):
    items = {}

    item_data = json.load(open("data/" + item_file))

    for item in item_data:
        items[int(item)] = {'name': item_data[item]['name'],
                            'icon': transform.scale(image.load("textures/items/" + item_data[item]['icon']).convert_alpha(), (32, 32)),
                            'maxstack': item_data[item]['maxstack']}

    return items


def create_item_dictionary(*libraries):
    item_lib = {}

    for di in libraries:
        for item in di:
            item_lib[item] = [di[item]['name'], di[item]['icon'], di[item]['maxstack']]

    return item_lib


def commandline_in(commandline_queue, fn, address, chat_queue):
    rah.rahprint('Ready for input.')
    sys.stdin = os.fdopen(fn)

    while True:
        commandline_queue.put(((10, chat_queue.get()), address))


def pickup_item(inventory, hotbar, Nitem, item_lib):
    item_location = ''
    inventory_type = ''
    for item in range(len(hotbar)):
        if hotbar[item][0] == Nitem and hotbar[item][1] < item_lib[hotbar[item][0]][2]:
            hotbar[item][1] += 1
            return inventory, hotbar
        elif hotbar[item][0] == 0 and inventory_type == '':
            item_location = item
            inventory_type = 'hotbar'

    for row in range(len(inventory)):
        for item in range(len(inventory[row])):
            if inventory[row][item][0] == Nitem and inventory[row][item][1] < item_lib[inventory[row][item][0]][2]:
                inventory[row][item][1] += 1
                return inventory, hotbar
            elif inventory[row][item][0] == 0 and inventory_type == '':
                item_location = [row, item]
                inventory_type = 'inventory'

    if inventory_type == 'hotbar':
        hotbar[item_location] = [Nitem, 1]
    elif inventory_type == 'inventory':
        inventory[item_location[0]][item_location[1]] = [Nitem, 1]

    return inventory, hotbar


def game(surf, username, token, host, port, size, music_enable):
    def quit_game():
        send_queue.put(((9, block_size), SERVERADDRESS))
        time.wait(50)
        sender.terminate()
        receiver.terminate()
        commandline.terminate()

    def get_neighbours(x, y):
        return [world[x + 1, y], world[x - 1, y], world[x, y + 1], world[x, y - 1]]

    def render_world():
        for x in range(0, size[0] + block_size + 1, block_size):  # Render blocks
            for y in range(0, size[1] + block_size + 1, block_size):
                block = world[(x + x_offset) // block_size][(y + y_offset) // block_size]

                if len(block_properties) > block > 0:
                    surf.blit(block_properties[block]['texture'],
                              (x - x_offset % block_size, y - y_offset % block_size))

                    if breaking_block and current_breaking[1] == (x + x_offset) // block_size \
                            and current_breaking[2] == (y + y_offset) // block_size:
                        percent_broken = (current_breaking[3] / block_properties[current_breaking[0]]['hardness']) * 10
                        surf.blit(breaking_animation[int(percent_broken)],
                                  (x - x_offset % block_size, y - y_offset % block_size))

                        # elif block < 0:
                        #     draw.rect(surf, (100, 100, 100),
                        #               (x - x_offset % block_size, y - y_offset % block_size, block_size, block_size))

    def render_hotbar(hotbar_slot):
        surf.blit(hotbar, hotbar_rect)
        for item in range(9):
            if Rect(hotbar_rect[0] + (32 + 8) * item + 6, size[1] - 32 - 6, 32, 32).collidepoint(mx, my) and mb[0]:
                hotbar_slot = item

            if hotbar_items[item][1] != 0:
                surf.blit(item_lib[hotbar_items[item][0]][1], (hotbar_rect[0] + (32 + 8) * item + 6, size[1] - 32 - 6))
                if hotbar_items[item][1] > 1:
                    surf.blit(rah.text(str(hotbar_items[item][1]), 10),
                              (hotbar_rect[0] + (32 + 8) * item + 6, size[1] - 32 - 6))

            if len(hotbar_items[item]) == 3:
                draw.rect(surf, (0, 0, 0), (hotbar_rect[0] + (32 + 8) * item + 10, size[1] - 10, 24, 2))
                draw.rect(surf, (255, 255, 0), (hotbar_rect[0] + (32 + 8) * item + 10, size[1] - 10, int(24 * hotbar_items[item][2] // tool_properties[hotbar_items[item][0]]['durability']), 2))

        surf.blit(selected, (hotbar_rect[0] + (32 + 8) * hotbar_slot, size[1] - 32 - 12))

        if hotbar_items[hotbar_slot][0] != 0:
            block_name = rah.text(str(item_lib[hotbar_items[hotbar_slot][0]][0]), 13)
            surf.blit(block_name, (size[0] // 2 - block_name.get_width() // 2, size[1] - 60))

    # Loading Screen
    # =====================================================================
    display.set_caption("RahCraft")

    # Setting Up Socket I/O and Multiprocessing
    # =====================================================================
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SERVERADDRESS = (host, port)

    send_queue = Queue()
    message_queue = Queue()
    chat_queue = Queue()

    sender = Process(target=player_sender, args=(send_queue, server))
    sender.start()

    receiver = Process(target=receive_message, args=(message_queue, server))
    receiver.start()

    fn = sys.stdin.fileno()
    commandline = Process(target=commandline_in, args=(send_queue, fn, SERVERADDRESS, chat_queue))
    commandline.start()
    cmd_in = ""

    block_size = 25
    build = 'RahCraft v0.1.1 EVALUATION'

    # Chat
    # =====================================================================
    chat = menu.TextBox(20, size[1] - 120, size[0] - 50, 40, '')
    chat_content = ''
    chat_list = []

    # Loading Textures
    # =====================================================================
    block_properties = load_blocks("block.json", block_size)
    tool_properties = load_tools("tools.json")
    item_properties = load_items("items.json")

    item_lib = create_item_dictionary(block_properties, tool_properties, item_properties)
    rah.rahprint(item_lib)
    breaking_animation = [
        transform.scale(image.load("textures/blocks/destroy_stage_" + str(i) + ".png"), (20, 20)).convert_alpha() for i
        in range(10)]

    tint = Surface(size)
    tint.fill((0, 0, 0))
    tint.set_alpha(99)

    # Receiving First Messages, Initing World, and Player
    # =====================================================================

    clock = time.Clock()
    dir = 5
    slider_x = 0

    for cycle in range(1001):
        server.sendto(pickle.dumps([0, username, token]), SERVERADDRESS)

        if cycle == 1000:
            return 'information', '\n\n\n\n\nUnable to connect to server\nTimed out', 'server_picker'

        rah.wallpaper(surf, size)

        connecting_text = rah.text("Connecting to %s:%i..." % (host, port), 15)

        surf.blit(connecting_text,
                  rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

        tile_w = size[0]//8

        slider_x += dir

        if slider_x <= 0 or slider_x >= size[0]//2 - tile_w:
            dir *= -1

        draw.rect(surf, (0,0,0), (size[0]//4, size[1]//2 + 40, size[0]//2, 10))
        draw.rect(surf, (0, 255, 0), (size[0]//4 + slider_x, size[1]//2 + 40, tile_w,10))

        display.update()

        try:
            first_message = message_queue.get_nowait()
            if first_message[0] == 400:
                sender.terminate()
                receiver.terminate()
                commandline.terminate()
                return 'information', first_message[1], 'server_picker'
            elif first_message[0] == 0:
                break

        except:
            pass

        clock.tick(500)

    world_size_x, world_size_y, player_x_, player_y_, hotbar_items, inventory_items, r_players = first_message[1:]

    rah.rahprint("player done")

    reach = 5

    player_x = int(float(player_x_) * 20 - size[0] // 2)
    player_y = int(float(player_y_) * 20 - size[1] // 2)

    world = np.array([[-1] * (world_size_y + 40) for _ in range(world_size_x)])

    local_player = player.Player(player_x, player_y, block_size - 5, 2 * block_size - 5, block_size, 5,
                                 (K_a, K_d, K_w, K_s, K_SPACE))

    x_offset = local_player.rect.x - size[0] // 2 + block_size // 2
    y_offset = local_player.rect.y - size[1] // 2 + block_size // 2

    remote_players = {}
    x, y = 0, 0

    send_queue.put([[2, x_offset // block_size, y_offset // block_size, size, block_size], SERVERADDRESS])

    while True:
        world_msg = message_queue.get()
        rah.rahprint(world_msg)
        if world_msg[0] == 2:
            break

    world[world_msg[1] - 5:world_msg[1] + size[0] // block_size + 5,
    world_msg[2] - 5:world_msg[2] + size[1] // block_size + 5] = np.array(world_msg[3], copy=True)

    # Init Existing Remote Players
    # =====================================================================
    for Rp in r_players:
        remote_players[Rp] = player.RemotePlayer(Rp, r_players[Rp][0], r_players[Rp][1], block_size - 5,
                                                 2 * block_size - 5)

    # Initing Pygame Components
    # =====================================================================
    clock = time.Clock()

    # Initing Ticks and Sky
    # =====================================================================
    TICKEVENT = USEREVENT + 1
    tick_timer = time.set_timer(TICKEVENT, 50)
    current_tick = 0

    # sky = transform.scale(image.load("textures/sky/sky.png"), (5600, 800))
    sun = transform.scale(image.load("textures/sky/sun.png"), (100, 100))
    moon = transform.scale(image.load("textures/sky/moon.png"), (100, 100))
    sky_tick = 1

    SKYTICKDEFAULT = 120

    # Initing Anti-Lag
    # =====================================================================
    block_request = set()
    render_request = set()

    # Initing Pausing/Inventories
    # =====================================================================
    paused = False

    fly = False
    inventory_visible = False
    chat_enable = False
    debug = True

    pause_list = [[0, 'unpause', "Back to game"],
                  [1, 'options', "Options"],
                  [2, 'menu', "Exit"]]

    pause_menu = menu.Menu(pause_list, 0, 0, size[0], size[1])

    # Initing Block Breaking
    # =====================================================================
    current_breaking = []
    breaking_block = False

    # Init Inventory
    # =====================================================================
    hotbar = image.load("textures/gui/toolbar/toolbar.png").convert()
    selected = image.load("textures/gui/toolbar/selected.png").convert_alpha()

    normal_font = font.Font("fonts/minecraft.ttf", 14)

    inventory_object = menu.Inventory(0, 0, size[0], size[1])

    hotbar_rect = (size[0] // 2 - hotbar.get_width() // 2, size[1] - hotbar.get_height())
    hotbar_slot = 1

    INVENTORY_KEYS = {str(x) for x in range(1, 10)}

    # Initing Sound
    # =====================================================================
    sound_types = [stype[6:-1] for stype in glob.glob('sound/*/')]

    sound = {sound_type: {} for sound_type in sound_types}

    for stype in sound_types:

        sound_list = glob.glob('sound/%s/*.ogg' % stype)

        sound_blocks = [sound.replace('\\', '/').split("/")[-1][:-5] for sound in sound_list]

        for block in sound_blocks:
            local_sounds = []

            for sound_dir in sound_list:
                if block in sound_dir:
                    local_sounds.append(sound_dir)

            sound[stype][block] = local_sounds

    block_step = None

    # Crafting
    # =====================================================================

    crafting_object = menu.Crafting(size[0], size[1])

    crafting = False

    current_gui = ''

    # Block highlight
    # =====================================================================
    highlight_good = Surface((block_size, block_size))
    highlight_good.fill((255, 255, 255))
    highlight_good.set_alpha(50)

    highlight_bad = Surface((block_size, block_size))
    highlight_bad.fill((255, 0, 0))
    highlight_bad.set_alpha(90)
    inventory_updated = False

    sky_diming = False

    try:
        while True:
            release = False
            on_tick = False
            block_broken = False
            tick_per_frame = max(clock.get_fps() / 20, 1)
            r_click = False
            l_click = False
            pass_event = None
            inventory_updated = False

            for e in event.get():
                pass_event = e
                if e.type == QUIT:
                    quit_game()
                    return 'menu'

                    # elif e.type == ACTIVEEVENT:
                    #     if e.state == 1:
                    #         paused = True
                    #

                elif e.type == MOUSEBUTTONDOWN and not paused:
                    if e.button == 1:
                        l_click = True
                    if e.button == 3:
                        r_click = True

                    if e.button == 4:

                        hotbar_slot = max(-1, hotbar_slot - 1)

                        if hotbar_slot == -1:
                            hotbar_slot = 8

                    elif e.button == 5:

                        hotbar_slot = min(9, hotbar_slot + 1)

                        if hotbar_slot == 9:
                            hotbar_slot = 0

                elif e.type == MOUSEBUTTONUP and e.button == 1:
                    release = True

                elif e.type == KEYDOWN:

                    if e.key == K_F3:
                        debug = not debug

                    if e.key == K_SLASH and not current_gui:
                        chat_enable = True
                        current_gui = 'CH'

                    if chat_enable and e.key == K_RETURN:
                        chat_queue.put(chat_content)
                        chat.content = ''
                        chat_enable = False
                        current_gui = ''

                    if e.key == K_ESCAPE:
                        if current_gui == 'C':
                            inventory_updated = True
                            crafting = False
                            current_gui = ''
                        elif current_gui == 'I':
                            inventory_updated = True
                            inventory_visible = False
                            current_gui = ''
                        elif current_gui == 'CH':
                            chat.content = ''
                            chat_enable = False
                            current_gui = ''
                        elif current_gui == '' or current_gui == 'P':
                            paused = not paused
                            if paused:
                                current_gui = 'P'
                            else:
                                current_gui = ''

                    elif not paused and current_gui != 'CH':
                        if e.unicode in INVENTORY_KEYS:
                            hotbar_slot = int(e.unicode) - 1

                        if e.key == K_f:
                            fly = not fly

                        if e.key == K_r:
                            local_player.rect.y -= 40

                        if e.key == K_e and current_gui == '' or current_gui == 'I':
                            if current_gui == 'I':
                                inventory_updated = True

                            inventory_visible = not inventory_visible

                            if inventory_visible:
                                current_gui = 'I'
                            else:
                                current_gui = ''

                elif e.type == VIDEORESIZE:
                    surf = display.set_mode((e.w, e.h), RESIZABLE)
                    size = ((e.w, e.h))

                    chat = menu.TextBox(20, size[1] - 120, size[0] - 50, 40, '')
                    pause_menu = menu.Menu(pause_list, 0, 0, size[0], size[1])
                    inventory_object = menu.Inventory(0, 0, size[0], size[1])
                    hotbar_rect = (size[0] // 2 - hotbar.get_width() // 2, size[1] - hotbar.get_height())
                    crafting_object = menu.Crafting(size[0], size[1])

                    tint = Surface(size)
                    tint.fill((0, 0, 0))
                    tint.set_alpha(99)

                elif e.type == TICKEVENT:
                    event.clear(TICKEVENT)
                    tick_timer = time.set_timer(TICKEVENT, 50)

                    on_tick = True
                    current_tick += 1
                    if current_tick == 20:
                        current_tick = 0

            x_offset = local_player.rect.x - size[0] // 2 + block_size // 2
            y_offset = local_player.rect.y - size[1] // 2 + block_size // 2

            block_clip = (
                local_player.rect.x // block_size * block_size, local_player.rect.y // block_size * block_size)
            offset_clip = Rect((x_offset // block_size, y_offset // block_size, 0, 0))

            # if x_offset <= 0:
            #     x_offset = 1
            # elif x_offset >= world_size_x:
            #     x_offset = world_size_x - 1
            #
            # if y_offset >= world_size_y:
            #     y_offset = world_size_y - 1
            # elif y_offset <= 0:
            #     y_offset = 1

            if inventory_updated:

                send_queue.put(([(5, inventory_items, hotbar_items), SERVERADDRESS]))
                inventory_updated = False
            if on_tick:
                send_queue.put(([(1, local_player.rect.x, local_player.rect.y), SERVERADDRESS]))

            displaying_world = world[offset_clip.x:offset_clip.x + size[0] // block_size + 5,
                               offset_clip.y:offset_clip.y + size[1] // block_size + 5]
            update_cost = displaying_world.flatten()
            update_cost = np.count_nonzero(update_cost == -1)

            if update_cost > 0 and on_tick and (offset_clip.x, offset_clip.y) not in render_request:
                send_queue.put([[2, offset_clip.x, offset_clip.y, size, block_size], SERVERADDRESS])
                render_request.add((offset_clip.x, offset_clip.y))
            # ===================Decode Message======================

            try:
                server_message = message_queue.get_nowait()
                command, message = server_message[0], server_message[1:]

                print(message)

                if command == 1:
                    remote_username, current_x, current_y, tp = message

                    # if remote_username == username and tp:
                    #
                    #     x_offset, y_offset = current_x, current_y
                    #     local_player.rect.x, local_player.rect.y = x_offset + size[0] // 2 + block_size // 2, y_offset + size[1] // 2 + block_size // 2
                    #
                    #     local_player.update(surf, x_offset, y_offset, fly, current_gui, block_clip, world, block_size,
                    #                         block_properties)

                    if remote_username in remote_players:
                        remote_players[remote_username].calculate_velocity((current_x, current_y), tick_per_frame)
                        remote_players[remote_username].calculate_velocity(
                            (current_x * block_size, current_y * block_size), tickPerFrame)

                    else:
                        if type(current_y) is str:
                            current_x = int(current_x) * 20
                            current_y = int(current_y) * 20

                        remote_players[remote_username] = player.RemotePlayer(remote_username, current_x, current_y,
                                                                              block_size - 5, 2 * block_size - 5)

                elif command == 2:
                    chunk_position_x, chunk_position_y, world_chunk = message
                    world[chunk_position_x - 5:chunk_position_x + size[0] // block_size + 5,
                    chunk_position_y - 5:chunk_position_y + size[1] // block_size + 5] = np.array(world_chunk,
                                                                                                  copy=True)

                    if (chunk_position_x, chunk_position_y) in render_request:
                        render_request.remove((chunk_position_x, chunk_position_y))

                elif command == 3:
                    pos_x, pos_y = message
                    world[pos_x, pos_y] = 0

                    if (pos_x, pos_y) in block_request:
                        block_request.remove((pos_x, pos_y))

                elif command == 4:
                    pos_x, pos_y, block = message
                    world[pos_x, pos_y] = block

                    if (pos_x, pos_y) in block_request:
                        block_request.remove((pos_x, pos_y))

                elif command == 6:
                    slot, meta_data = message

                    hotbar_items[slot] = meta_data[:]

                elif command == 7:
                    slot, meta_data = message

                    inventory_items[slot] = meta_data[:]

                elif command == 9:
                    remote_username = message[0]

                    del remote_players[remote_username]

                elif command == 10:
                    chat_list.append(message[0])

                elif command == 11:
                    quit_game()
                    return 'information', message[0], 'menu'

                elif command == 100:
                    send_time, tick = message

                    tick_offset = (round(ti.time(), 3) - send_time) * 20

                    sky_tick = tick_offset + tick

                    for repeat in range(5):
                        send_queue.put(([(101, username), SERVERADDRESS]))

            except:
                pass

            # Adding Sky
            # =======================================================
            if on_tick:
                if not sky_diming:
                    sky_tick += 100
                else:
                    sky_tick -= 100

            if sky_tick > 12000:
                sky_diming = True
                sky_tick = sky_tick - (sky_tick-12000)
            elif sky_tick < 0:
                sky_diming = False
                sky_tick = sky_tick + abs(sky_tick)

                rah.rahprint("Reset")

            surf.fill(int(sky_tick/47))

            # for y in range(size[1]):
            #
            #     r = 0
            #     g = 0
            #     b = int(((y_offset // block_size)/world_size_y) * 255)
            #
            #     draw.line(surf, (r, g, b), (0, y), (size[0], y), 1)

            # surf.blit(sky, (int(0 - 4800 * (sky_tick % 24000) / 24000), max(y_offset // 2 - 400, -200)))
            surf.blit(sun, (int(5600 - 4800 * (sky_tick % 24000) / 24000), max(y_offset // 16 - 50, -200)))
            surf.blit(moon, (int(2800 - 4800 * (sky_tick % 24000) / 24000), max(y_offset // 16 - 50, -200)))

            # Render World
            # =======================================================
            try:
                render_world()
            except:
                pass

            local_player.update(surf, x_offset, y_offset, fly, current_gui, block_clip, world, block_size,
                                block_properties)

            under_block = (offset_clip.x, y_offset // block_size + 1)

            if world[under_block] > 0 and block_step != under_block:
                rah.load_sound(sound['step'][block_properties[world[under_block]]['sound']])

                block_step = under_block

            # ==========================Mouse Interaction=================================
            mb = mouse.get_pressed()
            mx, my = mouse.get_pos()

            hover_x, hover_y = ((mx + x_offset) // block_size, (my + y_offset) // block_size)
            block_clip_cord = (block_clip[0] // block_size, block_clip[1] // block_size)

            if not current_gui:
                if mb[0] == 0:
                    current_breaking = []
                    breaking_block = False

                elif mb[0] == 1:
                    if not breaking_block and world[hover_x, hover_y] > 0 and (
                            hover_x, hover_y) not in block_request and hypot(hover_x - block_clip_cord[0],
                                                                             hover_y - block_clip_cord[1]) <= reach:
                        breaking_block = True
                        current_breaking = [world[hover_x, hover_y], hover_x, hover_y, 1]
                        if current_breaking[3] >= block_properties[current_breaking[0]]['hardness']:
                            block_broken = True

                    elif breaking_block and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                        if hover_x == current_breaking[1] and hover_y == current_breaking[2]:

                            if hotbar_items[hotbar_slot][0] in tool_properties:
                                current_tool = hotbar_items[hotbar_slot][0]

                                if tool_properties[current_tool]['type'] == \
                                        block_properties[world[hover_x, hover_y]]['tool']:
                                    current_breaking[3] += tool_properties[current_tool]['bonus']
                                else:
                                    current_breaking[3] += tool_properties[current_tool]['speed']
                            else:
                                current_breaking[3] += 1

                            if current_breaking[3] >= block_properties[current_breaking[0]]['hardness']:
                                block_broken = True

                                rah.load_sound(sound['step'][block_properties[world[hover_x, hover_y]]['sound']])

                        else:
                            breaking_block = False
                            current_breaking = []

                    if block_broken:

                        rah.load_sound(sound['dig'][block_properties[world[hover_x, hover_y]]['sound']])

                        if hotbar_items[hotbar_slot][0] in tool_properties:
                            if len(hotbar_items[hotbar_slot]) == 2:
                                hotbar_items[hotbar_slot].append(tool_properties[hotbar_items[hotbar_slot][0]]['durability'])
                            else:
                                hotbar_items[hotbar_slot][2] -= 1
                                if hotbar_items[hotbar_slot][2] == 0:
                                    hotbar_items[hotbar_slot] = [0, 0]

                        print(hotbar_items)

                        if block_properties[world[hover_x, hover_y]]['tool-required']:
                            if hotbar_items[hotbar_slot][0] in tool_properties:
                                current_tool = hotbar_items[hotbar_slot][0]
                                if tool_properties[current_tool]['type'] == block_properties[world[hover_x, hover_y]][
                                    'tool']:
                                    inventory_items, hotbar_items = pickup_item(inventory_items, hotbar_items,
                                                                                block_properties[
                                                                                    world[hover_x, hover_y]]['drop'],
                                                                                item_lib)
                        else:
                            inventory_items, hotbar_items = pickup_item(inventory_items, hotbar_items,
                                                                        block_properties[world[hover_x, hover_y]][
                                                                            'drop'], item_lib)

                        inventory_updated = True

                        block_request.add((hover_x, hover_y))
                        send_queue.put(((3, hover_x, hover_y), SERVERADDRESS))

                        current_breaking = []
                        breaking_block = False

                if mb[2] == 1 and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                    if world[hover_x, hover_y] == 10 and current_gui == '':
                        crafting = not crafting
                        current_gui = 'C'
                    elif world[hover_x, hover_y] == 0 and sum(get_neighbours(hover_x, hover_y)) > 0 and (
                            hover_x, hover_y) not in block_request and on_tick and hotbar_items[hotbar_slot][1] != 0 and \
                                    hotbar_items[hotbar_slot][0] in block_properties:
                        block_request.add((hover_x, hover_y))
                        send_queue.put(
                            ((4, hover_x, hover_y, hotbar_items[hotbar_slot][0], hotbar_slot), SERVERADDRESS))

                        hover_sound = block_properties[hotbar_items[hotbar_slot][0]]

                        if hover_sound['sound'] != 'nothing':
                            rah.load_sound(sound['dig'][hover_sound['sound']])

                if mb[1] == 1 and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                    hotbar_items[hotbar_slot] = [world[hover_x, hover_y], 1]

                if hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                    surf.blit(highlight_good, ((mx + x_offset) // block_size * block_size - x_offset,
                                               (my + y_offset) // block_size * block_size - y_offset))
                else:
                    surf.blit(highlight_bad, ((mx + x_offset) // block_size * block_size - x_offset,
                                              (my + y_offset) // block_size * block_size - y_offset))

            for remote in remote_players:
                remote_players[remote].update(surf, x_offset, y_offset)

            # ====================Inventory/hotbar========================

            render_hotbar(hotbar_slot)

            # ===================Pausing====================================
            if paused:
                surf.blit(tint, (0, 0))

                text_surface = rah.text('Game Paused', 20)
                surf.blit(text_surface, (size[0] // 2 - text_surface.get_width() // 2, 50))

                nav_update = pause_menu.update(surf, release, mx, my, mb)

                if nav_update:
                    if nav_update == 'unpause':
                        paused = False
                    elif nav_update == 'menu':
                        quit_game()
                        return 'menu'
                    else:
                        return nav_update

            elif inventory_visible:
                surf.blit(tint, (0, 0))
                inventory_object.update(surf, mx, my, mb, l_click, r_click, inventory_items, hotbar_items, item_lib)

            elif crafting:
                surf.blit(tint, (0, 0))

                crafting_object.update(surf, mx, my, mb, l_click, r_click, inventory_items, hotbar_items, item_lib)

            if not paused:
                if key.get_pressed()[K_TAB]:

                    players = ['RahCraft',
                               '---------',
                               username] + [player for player in remote_players]

                    tab_back = Surface((200, len(players) * 30 + 10),
                                       SRCALPHA)

                    tab_back.fill(Color(75, 75, 75, 150))

                    surf.blit(tab_back, (size[0] // 2 - 100, 40))

                    for y in range(0, len(players)):
                        about_text = normal_font.render(players[y], True, (255, 255, 255))
                        surf.blit(about_text, (size[0] // 2 - about_text.get_width() // 2, 50 + y * 20))

            text_height = rah.text("QWERTYRAHMA", 10).get_height()

            while len(chat_list) * text_height > (5 * size[1]) // 8:
                del chat_list[0]

            for line in range(len(chat_list)):
                surf.blit(rah.text(chat_list[line], 10), (20, line * (text_height + 3)))

            if chat_enable:
                chat_content = chat.update(pass_event)
                chat.draw(surf, '')

            if debug:

                debug_list = ["%s" % build,
                              "FPS: %i" % round(clock.get_fps(), 2),
                              "X:%i Y:%i" % (offset_clip.x, y_offset // block_size),
                              "Block Size: %i" % block_size,
                              "Hotbar Slot: %i" % hotbar_slot,
                              "Block Selected: %s" % str(item_lib[hotbar_items[hotbar_slot][0]][0]),
                              "Mouse Pos: %i, %i" % ((mx + x_offset) // block_size, (my + y_offset) // block_size),
                              "Update Cost: %i" % update_cost,
                              "Time: %s" % sky_tick,
                              "Token: %s" % token[0:10]]

                for y in range(len(debug_list)):
                    about_text = rah.text(debug_list[y], 15)
                    surf.blit(about_text, (size[0] - about_text.get_width() - 10, 10 + y * 20))

            clock.tick(120)
            display.set_caption("RahCraft // FPS - {0}".format(clock.get_fps()))
            display.update()

    except:
        quit_game()
        return 'crash', traceback.format_exc(), 'menu'


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5276

    size = (800, 500)
    surf = display.set_mode(size)

    font.init()

    game(surf, "6", host, port, size)
