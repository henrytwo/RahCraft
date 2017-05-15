from pygame import *
from multiprocessing import *
#from player import *
import numpy as np
import socket
import pickle
import components.rahma as rah
import components.player2 as plr

def player_sender(send_queue, server):
    print('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    print('Ready to receive command...')

    while True:
        msg = server.recvfrom(16384)
        message_queue.put(pickle.loads(msg[0]))


def load_blocks(block_file):
    blocks = {}

    block_file = open("data/" + block_file).readlines()

    for line_number in range(len(block_file)):
        block_type, inner_block, outline, block_image, hardness = block_file[line_number].strip("\n").split(" // ")
        blocks[line_number] = [block_type, (int(x) for x in inner_block.split(",")), (int(x) for x in outline.split(",")), transform.scale(image.load("textures/blocks/" + block_image), (20, 20)), int(hardness)]

    return blocks


def game(screen, username, host, port, size):
    print('Starting game')

    font.init()

    def quit_game():
        send_queue.put(((9,), _server))
        time.wait(50)
        sender.terminate()
        receiver.terminate()

    def get_neighbours(x, y):
        return [world[x + 1, y], world[x - 1, y], world[x, y + 1], world[x, y - 1]]

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _server = (host, port)

    send_queue = Queue()
    message_queue = Queue()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))

    block_texture = load_blocks("block.rah")
    connecting_text = rah.text("Connecting to %s:%i..." % (host, port), 30)
    screen.blit(connecting_text, rah.center(0, 0, size[0], size[1], connecting_text.get_width(), connecting_text.get_height()))

    display.update()

    clock = time.Clock()

    print("Client connecting to %s:%i" % _server)

    server.sendto(pickle.dumps([0, username]), _server)

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

    world_size_x, world_size_y, player_x, player_y, players = first_message[1:]

    block_size = 20
    reach = 5*block_size
    player_x = player_x*20 - size[0]//2
    player_y = player_y*20 - size[1]//2

    world = np.array([[-1] * world_size_y for _ in range(world_size_x)])

    hotbar_slot = 1

    inventory = [[-1] * 6 for x in range(7)]
    local_player = plr.Player(player_x, player_y, block_size, block_size, (K_a, K_d, K_w, K_s))
    x_offset = local_player.rect.x - size[0] // 2 + block_size // 2
    y_offset = local_player.rect.y - size[1] // 2 + block_size // 2

    remote_players = {}

    _inventory_keys = {str(x) for x in range(1, 10)}

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

    send_queue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])

    while True:
        world_msg = message_queue.get()
        print(world_msg)
        if world_msg[0] == 2:
            break

    world[world_msg[1] - 5:world_msg[1] + 45, world_msg[2] - 5:world_msg[2] + 31] = np.array(world_msg[3], copy=True)

    print("ini done")


    while True:
        on_tick = False
        block_broken = False
        tickPerFrame = max(clock.get_fps() / 20, 1)
        for e in event.get():
            if e.type == QUIT:
                quit_game()
                return 'menu'

            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    click = True

                elif e.button == 4:
                    hotbar_slot = max(-1, hotbar_slot - 1)

                    if hotbar_slot == -1:
                        hotbar_slot = 8

                elif e.button == 5:
                    hotbar_slot = min(9, hotbar_slot + 1)

                    if hotbar_slot == 0:
                        hotbar_slot = 0

            elif e.type == MOUSEBUTTONUP and e.button == 1:
                release = True

            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    if paused:
                        paused = False
                    else:
                        paused = True

                elif not paused:
                    if e.unicode in _inventory_keys:
                        hotbar_slot = int(e.unicode) - 1

                    if e.key == K_f:
                        if fly:
                            fly = False
                        else:
                            fly = True

            elif e.type == TICKEVENT:
                event.clear(TICKEVENT)
                tickTimer = time.set_timer(TICKEVENT, 50)

                on_tick = True
                current_tick += 1
                if current_tick == 20:
                    current_tick = 0

        x_offset = local_player.rect.x - size[0]//2 + block_size//2
        y_offset = local_player.rect.y - size[1]//2 + block_size//2
        
        if on_tick:
            send_queue.put(([(1, local_player.rect.x, local_player.rect.y), _server]))


        displaying_world = world[x_offset // block_size:x_offset // block_size + 41, y_offset // block_size:y_offset // block_size + 26]
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
                username, current_x, current_y, = message
                if username in players:
                    past_x, past_y = players[username][0]

                    players[username][1] = ((current_x - past_x) // tickPerFrame, (current_y - past_y) // tickPerFrame)

                    if sum(players[username][1]) < 3:
                        players[username][1] = (0, 0)
                        players[username][0] = [past_x, past_y]

                else:
                    players[username] = [[current_x, current_y], (0, 0)]

            elif command == 2:
                chunk_positionX, chunk_positionY, world_chunk = message

                world[chunk_positionX - 5:chunk_positionX + 45, chunk_positionY - 5:chunk_positionY + 31] = np.array(world_chunk, copy=True)

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

            elif command == 9:
                username = message[0]

                del players[username]

        except:
            pass

        #testing==================================================

        mb = mouse.get_pressed()
        mx, my = mouse.get_pos()

        hover_x, hover_y = ((mx + x_offset) // block_size, (my + y_offset) // block_size)

        display.set_caption("Minecrap Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " A: " + str(x_offset // block_size) + " Y:" + str(y_offset // block_size) + " Size:" + str(
            block_size) + " Block Selected:" + str(hotbar_slot) + "  // " + block_texture[hotbar_slot][0] +
                            "Mouse: " + str((mx + x_offset) // block_size) + " " + str((my + y_offset) // block_size))

        if mb[0] == 0:
            current_breaking = []
            breaking_block = False

        elif mb[0] == 1 and mb[2] == 0:
            if not breaking_block and world[hover_x, hover_y] != 0 and (hover_x, hover_y) not in block_request:
                breaking_block = True
                current_breaking = [world[hover_x, hover_y], hover_x, hover_y, 1]
                if current_breaking[3] >= block_texture[current_breaking[0]][4]:
                    block_broken = True

            elif breaking_block:
                if hover_x == current_breaking[1] and hover_y == current_breaking[2]:
                    current_breaking[3] += 1

                    if current_breaking[3] >= block_texture[current_breaking[0]][4]:
                        block_broken = True
                else:
                    breaking_block = False
                    current_breaking = []

            if block_broken:
                block_request.add((hover_x, hover_y))
                send_queue.put(((3, hover_x, hover_y), _server))

                current_breaking = []
                breaking_block = False

        if mb[2] == 1:
            if world[hover_x, hover_y] == 0 and sum(get_neighbours(hover_x, hover_y)) > 0 and (hover_x, hover_y) not in block_request and on_tick:
                block_request.add((hover_x, hover_y))
                send_queue.put(((4, hover_x, hover_y, hotbar_slot), _server))

        # ==================Render World==========================
        screen.fill((173, 216, 230))
        for x in range(0, size[0]+block_size+1, block_size):  # Render blocks
            for y in range(0, size[1]+block_size+1, block_size):
                block = world[(x + x_offset) // block_size][(y + y_offset) // block_size]

                if len(block_texture) > block > 0:
                    screen.blit(block_texture[block][3], (x - x_offset % block_size, y - y_offset % block_size))

                elif block < 0:
                    draw.rect(screen, (0, 0, 0), (x - x_offset % block_size, y - y_offset % block_size, block_size, block_size))

        surrounding_blocks = []

        block_clip = (local_player.rect.x//block_size*block_size, local_player.rect.y//block_size*block_size)

        for x_blocks in range(-1,2):
            for y_blocks in range(-1,2):
                if world[(block_clip[0]-x_blocks*block_size)//block_size, (block_clip[1]-y_blocks*block_size)//block_size] > 0:
                    surrounding_blocks.append(Rect(block_clip[0]-x_blocks*block_size, block_clip[1]-y_blocks*block_size, block_size, block_size))

        local_player.update(screen, surrounding_blocks, x_offset, y_offset, fly)
        display.update()
        clock.tick(60)


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5276

    size = (800, 500)
    screen = display.set_mode(size)

    init()
    font.init()

    game(screen, "Ryan1", host, port)
