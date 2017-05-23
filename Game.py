from pygame import *
from multiprocessing import *
# from player import *
import numpy as np
import socket
import pickle
import components.rahma as rah
from math import *
import components.player2 as player2
import components.menu as menu
import time as ti
import glob
import traceback


def player_sender(send_queue, server):
    rah.rahprint('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    rah.rahprint('Ready to receive command...')

    while True:
        msg = server.recvfrom(16384)
        message_queue.put(pickle.loads(msg[0]))


def load_blocks(block_file):
    blocks = {}

    block_file = open("data/" + block_file).readlines()

    for line_number in range(len(block_file)):
        block_type, inner_block, outline, block_image, hardness, soundpack, collision = block_file[line_number].strip(
            "\n").split(" // ")
        blocks[line_number] = [block_type, (int(x) for x in inner_block.split(",")),
                               (int(x) for x in outline.split(",")),
                               transform.scale(image.load("textures/blocks/" + block_image).convert_alpha(), (20, 20)), int(hardness),
                               soundpack, collision,
                               transform.scale(image.load("textures/blocks/" + block_image).convert_alpha(), (32, 32))]

    return blocks


def invert(colour):
    return 255 - colour[0], 255 - colour[1], 255 - colour[2]


def inverted_rect(surf, block_size, width, rx, ry):
    try:
        for x in range(block_size):
            for y in range(width):
                surf.set_at((rx + x, ry + y), invert(surf.get_at((rx + x, ry + y))))
                surf.set_at((rx + x, ry + y + block_size - width),
                            invert(surf.get_at((rx + x, ry + y + block_size - width))))

        for y in range(block_size - width * 2):
            for x in range(width):
                surf.set_at((rx + x, ry + y + width), invert(surf.get_at((rx + x, ry + y + width))))
                surf.set_at((rx + x + block_size - width, ry + y + width),
                            invert(surf.get_at((rx + x + block_size - width, ry + y + width))))

    except:
        pass


def toggle(boolean):
    return not boolean


def game(surf, username, token, host, port, size, music_enable):
    rah.rahprint('Starting game')

    font.init()

    def quit_game():
        send_queue.put(((9, block_size), SERVER))
        time.wait(50)
        sender.terminate()
        receiver.terminate()

    def get_neighbours(x, y):
        return [world[x + 1, y], world[x - 1, y], world[x, y + 1], world[x, y - 1]]

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    SERVER = (host, port)

    send_queue = Queue()
    message_queue = Queue()

    block_size = 20

    tint = Surface(size)
    tint.fill((0, 0, 0))
    tint.set_alpha(99)

    block_properties = load_blocks("block.rah")
    breaking_animation = [
        transform.scale(image.load("textures/blocks/destroy_stage_" + str(i) + ".png"), (20, 20)).convert_alpha() for i
        in range(10)]

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    surf.blit(wallpaper, (0, 0))

    connecting_text = rah.text("Connecting to %s:%i..." % (host, port), 30)
    surf.blit(connecting_text,
              rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    display.update()

    clock = time.Clock()

    rah.rahprint("Client connecting to %s:%i" % SERVER)

    server.sendto(pickle.dumps([0, username, token]), SERVER)

    sender = Process(target=player_sender, args=(send_queue, server))
    sender.start()

    receiver = Process(target=receive_message, args=(message_queue, server))
    receiver.start()

    while True:
        first_message = message_queue.get()
        if first_message == (400,):
            sender.terminate()
            receiver.terminate()
            return "login"
        elif first_message[0] == 0:
            break

    world_size_x, world_size_y, player_x, player_y, hotbar_items, inventory_items, R_players = first_message[1:]

    rah.rahprint("player done")

    reach = 5
    player_x = int(player_x) * 20 - size[0] // 2
    player_y = int(player_y) * 20 - size[1] // 2

    world = np.array([[-1] * world_size_y for _ in range(world_size_x)])

    local_player = player2.Player(player_x, player_y, block_size - 5, 2 * block_size - 5, (K_a, K_d, K_w, K_s))
    x_offset = local_player.rect.x - size[0] // 2 + block_size // 2
    y_offset = local_player.rect.y - size[1] // 2 + block_size // 2

    remote_players = {}

    TICKEVENT = USEREVENT + 1
    tickTimer = time.set_timer(TICKEVENT, 50)
    current_tick = 0

    block_request = set()
    render_request = set()

    x, y = 0, 0
    paused = False

    current_breaking = []
    breaking_block = False

    fly = False
    inventory_visible = False

    send_queue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])

    while True:
        world_msg = message_queue.get()
        rah.rahprint(world_msg)
        if world_msg[0] == 2:
            break

    world[world_msg[1] - 5:world_msg[1] + 45, world_msg[2] - 5:world_msg[2] + 31] = np.array(world_msg[3], copy=True)

    pause_list = [[0, 'unpause', "Back to game"],
                  [1, 'assistance', "Help"],
                  [2, 'options', "Options"],
                  [3, 'about', "About"],
                  [4, 'menu', "Exit"]]

    pause_menu = menu.Menu(pause_list, 0, 0, size[0], size[1])

    # =============================init inventory==========================

    hotbar = image.load("textures/gui/toolbar/toolbar.png").convert()
    selected = image.load("textures/gui/toolbar/selected.png").convert_alpha()

    sky = transform.scale(image.load("textures/sky/sky.png"), (5600, 800))

    sun = transform.scale(image.load("textures/sky/sun.png"), (100, 100))
    moon = transform.scale(image.load("textures/sky/moon.png"), (100, 100))

    sound_list = glob.glob('sound/step/*.ogg')

    sound_groups = [sound.split("/")[-1] for sound in sound_list]

    sound = {}

    for sound_title in sound_groups:
        local_sounds = []

        for sound_dir in sound_list:
            if sound_title in sound_dir:
                local_sounds.append(sound_dir)

        sound[sound_title] = local_sounds

    rah.rahprint(sound)

    inventory_object = menu.Inventory(0, 0, size[0], size[1])

    hotbarRect = (size[0] // 2 - hotbar.get_width() // 2, size[1] - hotbar.get_height())
    hotbar_slot = 1

    INVENTORY_KEYS = {str(x) for x in range(1, 10)}

    rah.rahprint("ini done")

    # ==============================Sky=====================================
    DEFAULTSKYCOLOR = [135, 206, 235]
    sky_color = [-65, 6, 35]
    normalized_color = [max(x, 0) for x in sky_color]
    DEFAULT_BLUE = 235
    darken = False

    sky_tick = 1
    SKYTICKDEFAULT = 120

    # ==========================Crafting====================================
    crafting_object = menu.Crafting(size[0], size[1])

    crafting = False

    current_gui = ''

    try:

        # ====================Init remote players================================

        for Rp in R_players:
            remote_players[Rp] = player2.RemotePlayer(Rp, R_players[Rp][0], R_players[Rp][1], block_size - 5, 2 * block_size - 5)

        while True:

            release = False
            on_tick = False
            block_broken = False
            tickPerFrame = max(clock.get_fps() / 20, 1)
            r_click = False
            l_click = False

            for e in event.get():
                if e.type == QUIT:
                    quit_game()
                    return 'menu'

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
                    if e.key == K_ESCAPE:
                        if current_gui == 'C':
                            crafting = False
                            current_gui = ''
                        elif current_gui == 'I':
                            inventory_visible = False
                            current_gui == ''
                        elif current_gui == '' or current_gui == 'P':
                            paused = toggle(paused)
                            if paused:
                                current_gui = 'P'
                            else:
                                current_gui = ''

                    elif not paused:
                        if e.unicode in INVENTORY_KEYS:
                            hotbar_slot = int(e.unicode) - 1

                        if e.key == K_f:
                            fly = toggle(fly)

                        if e.key == K_e and current_gui == '' or current_gui == 'I':
                            inventory_visible = toggle(inventory_visible)

                            if inventory_visible:
                                current_gui = 'I'
                            else:
                                current_gui = ''

                elif e.type == TICKEVENT:
                    event.clear(TICKEVENT)
                    tickTimer = time.set_timer(TICKEVENT, 50)

                    on_tick = True
                    current_tick += 1
                    if current_tick == 20:
                        current_tick = 0

            x_offset = local_player.rect.x - size[0] // 2 + block_size // 2
            y_offset = local_player.rect.y - size[1] // 2 + block_size // 2
            block_clip = (local_player.rect.x // block_size * block_size, local_player.rect.y // block_size * block_size)

            if on_tick:
                send_queue.put(([(1, local_player.rect.x, local_player.rect.y), SERVER]))

            displaying_world = world[x_offset // block_size:x_offset // block_size + 41,
                                     y_offset // block_size:y_offset // block_size + 26]
            update_cost = displaying_world.flatten()
            update_cost = np.count_nonzero(update_cost == -1)

            if update_cost > 10 and on_tick and (x_offset // block_size, y_offset // block_size) not in render_request:
                send_queue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])

                render_request.add((x_offset // block_size, y_offset // block_size))
            # ===================Decode Message======================

            try:
                server_message = message_queue.get_nowait()
                command, message = server_message[0], server_message[1:]

                if command == 1:
                    username, current_x, current_y = message
                    if username in remote_players:
                        remote_players[username].calculate_velocity((current_x, current_y), tickPerFrame)
                    else:
                        if type(current_y) is str:
                            current_x = int(current_x) * 20
                            current_y = int(current_y) * 20

                        remote_players[username] = player2.RemotePlayer(username, current_x, current_y, block_size)

                elif command == 2:
                    chunk_positionX, chunk_positionY, world_chunk = message

                    world[chunk_positionX - 5:chunk_positionX + 45,
                          chunk_positionY - 5:chunk_positionY + 31] = np.array(world_chunk, copy=True)

                    if (chunk_positionX, chunk_positionY) in render_request:
                        render_request.remove((chunk_positionX, chunk_positionY))

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
                    username = message[0]

                    del remote_players[username]

                elif command == 100:
                    send_time, tick = message

                    tick_offset = (round(ti.time(), 3) - send_time) * 20

                    sky_tick = tick_offset + tick

            except:
                pass

            # testing==================================================

            mb = mouse.get_pressed()
            mx, my = mouse.get_pos()

            hover_x, hover_y = ((mx + x_offset) // block_size, (my + y_offset) // block_size)

            display.set_caption("Rahcraft Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " A: " + str(
                x_offset // block_size) + " Y:" + str(y_offset // block_size) + " Size:" + str(
                block_size) + " Block Selected:" + str(hotbar_slot) + "  // " + block_properties[hotbar_slot][0] +
                                "Mouse: " + str((mx + x_offset) // block_size) + " " + str(
                (my + y_offset) // block_size))

            block_clip_cord = (block_clip[0] // block_size, block_clip[1] // block_size)

            if not current_gui:
                if mb[0] == 0:
                    current_breaking = []
                    breaking_block = False

                elif mb[0] == 1:
                    if not breaking_block and world[hover_x, hover_y] != 0 and (
                            hover_x, hover_y) not in block_request and hypot(hover_x - block_clip_cord[0],
                                                                             hover_y - block_clip_cord[1]) <= reach:
                        breaking_block = True
                        current_breaking = [world[hover_x, hover_y], hover_x, hover_y, 1]
                        if current_breaking[3] >= block_properties[current_breaking[0]][4]:
                            block_broken = True

                    elif breaking_block and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                        if hover_x == current_breaking[1] and hover_y == current_breaking[2]:
                            current_breaking[3] += 1

                            if current_breaking[3] >= block_properties[current_breaking[0]][4]:
                                block_broken = True
                        else:
                            breaking_block = False
                            current_breaking = []

                    if block_broken:
                        block_request.add((hover_x, hover_y))
                        send_queue.put(((3, hover_x, hover_y), SERVER))

                        current_breaking = []
                        breaking_block = False

            # ==================Render World==========================
            if sky_tick % SKYTICKDEFAULT != 0:  # Change SKYTICKDEFAULT to a lower number to test
                if on_tick:
                    sky_tick += 1
            else:

                sky_tick += 1
                if sky_tick >= 24000:
                    sky_tick = 0

                    rah.rahprint("Reset")

            surf.fill((255, 0, 0))


            surf.blit(sky, (int(0 - 4800 * (sky_tick % 24000) / 24000), max(y_offset // 2 - 400, -200)))

            surf.blit(sun, (int(5600 - 4800 * (sky_tick % 24000) / 24000), max(y_offset // 16 - 50, -200)))
            surf.blit(moon, (int(2800 - 4800 * (sky_tick % 24000) / 24000), max(y_offset // 16 - 50, -200)))

            for x in range(0, size[0] + block_size + 1, block_size):  # Render blocks
                for y in range(0, size[1] + block_size + 1, block_size):
                    block = world[(x + x_offset) // block_size][(y + y_offset) // block_size]

                    if len(block_properties) > block > 0:
                        surf.blit(block_properties[block][3], (x - x_offset % block_size, y - y_offset % block_size))

                        if breaking_block and current_breaking[1] == (x + x_offset) // block_size and current_breaking[2] == (y + y_offset) // block_size:
                            percent_broken = (current_breaking[3] / block_properties[current_breaking[0]][4]) * 10
                            surf.blit(breaking_animation[int(percent_broken)],
                                      (x - x_offset % block_size, y - y_offset % block_size))

                    elif block < 0:
                        draw.rect(surf, (0, 0, 0),
                                  (x - x_offset % block_size, y - y_offset % block_size, block_size, block_size))

            if not current_gui:
                surrounding_blocks = []

                for x_shift, y_shift in player2.surrounding_shifts:

                    if block_properties[world[(block_clip[0] - x_shift * block_size) // block_size, (block_clip[1] - y_shift * block_size) // block_size]][6] == 'collide':
                        surrounding_blocks.append(Rect(block_clip[0] - x_shift * block_size, block_clip[1] - y_shift * block_size, block_size, block_size))

                local_player.update(surf, surrounding_blocks, x_offset, y_offset, fly, paused)

            if not current_gui:

                if mb[2] == 1 and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                    if world[hover_x, hover_y] == 10 and current_gui == '':
                        crafting = toggle(crafting)
                        current_gui = 'C'
                    elif world[hover_x, hover_y] == 0 and sum(get_neighbours(hover_x, hover_y)) > 0 and (
                            hover_x, hover_y) not in block_request and on_tick and hotbar_items[hotbar_slot][1] != 0:
                        block_request.add((hover_x, hover_y))
                        send_queue.put(((4, hover_x, hover_y, hotbar_items[hotbar_slot][0], hotbar_slot), SERVER))

                if mb[1] == 1 and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                    hotbar_items[hotbar_slot] = [world[hover_x, hover_y], 1]

                    if mb[1] == 1 and hypot(hover_x - block_clip_cord[0], hover_y - block_clip_cord[1]) <= reach:
                        hotbar_items[hotbar_slot] = world[hover_x, hover_y]

            for remote in remote_players:
                remote_players[remote].update(surf, x_offset, y_offset)

            # ====================Inventory/hotbar========================

            surf.blit(hotbar, hotbarRect)
            for item in range(9):
                if Rect(hotbarRect[0] + (32 + 8) * item + 6, size[1] - 32 - 6, 32, 32).collidepoint(mx, my) and mb[0]:
                    hotbar_slot = item

                if hotbar_items[item][1] != 0:
                    surf.blit(transform.scale(block_properties[hotbar_items[item][0]][3], (32, 32)),
                              (hotbarRect[0] + (32 + 8) * item + 6, size[1] - 32 - 6))
                    surf.blit(rah.text(str(hotbar_items[item][1]), 10),
                              (hotbarRect[0] + (32 + 8) * item + 6, size[1] - 32 - 6))

            surf.blit(selected, (hotbarRect[0] + (32 + 8) * hotbar_slot, size[1] - 32 - 12))

            # Pause surf
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

                inventory_object.update(surf, mx, my, mb, l_click, inventory_items, hotbar_items, block_properties)

            elif crafting:
                surf.blit(tint, (0, 0))

                crafting_object.update(surf, mx, my, mb, l_click, inventory_items, hotbar_items, block_properties)

            display.update()
            clock.tick(120)

    except:
        traceback.print_exc()
        quit_game()
        return 'menu'


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5276

    size = (800, 500)
    screen = display.set_mode(size)

    font.init()

    game(screen, "6", host, port, size)
