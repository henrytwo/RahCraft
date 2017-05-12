from pygame import *
from multiprocessing import *
from player import *
import numpy as np
import socket
import pickle

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

def game(screen, username, host, port):
    print('Starting game')

    def quit_game():
        send_queue.put(((9,), _server))
        time.wait(50)
        sender.terminate()
        receiver.terminate()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _server = (host, port)

    send_queue = Queue()
    message_queue = Queue()

    wallpaper = transform.scale(image.load("textures/menu/wallpaper.png"), (955, 500))
    screen.blit(wallpaper, (0, 0))
    # rahma.text(screen, "Connecting to %s:%i..." % (host, port), rahma.center(0, 0, 800, 500, ))

    '''
    block_list = [block.split(' // ') for block in open('block').read().split('\n')]

    for index in range(len(block_list)):
        block_list[index][1] = list(map(int, block_list[index][1].split(', ')))
        block_list[index][2] = list(map(int, block_list[index][2].split(', ')))
    '''

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

    world = np.array([[-1] * world_size_y for _ in range(world_size_x)])
    block_size = 20

    hotbar_slot = 1

    inventory = [[-1] * 6 for x in range(7)]
    local_player = Player(player_x, player_y, username, 20, 20, 1, size)  # Need player w and h

    remote_players = {}

    _inventory_keys = {str(x) for x in range(1, 10)}

    TICKEVENT = USEREVENT + 1
    tickTimer = time.set_timer(TICKEVENT, 50)

    block_request = set()
    render_request = set()

    while True:
        on_tick = False
        tickPerframe = max(clock.get_fps()/20, 1)
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
                    if e.key == K_t:
                        if advanced_graphics:
                            advanced_graphics = False
                        else:
                            advanced_graphics = True
                    elif e.unicode in _inventory_keys:
                        inventory_slot = int(e.unicode) - 1

            elif e.type == TICKEVENT:
                event.clear(TICKEVENT)
                tickTimer = time.set_timer(TICKEVENT, 50)

                on_tick = True
                current_tick += 1
                if current_tick == 20:
                    current_tick = 0

        local_player.update(screen)
        x_offset = local_player.rect.x
        y_offset = local_player.rect.y

        if on_tick:
            send_queue.put([(1, local_player.rect.x, local_player.rect.y)])

        local_player.update()

        #===================Decode Message======================

        try:
            server_message = message_queue.get_nowait()
            command, message = server_message[0], server_message[1:]

            if command == 1:
                username, current_x, current_y, = message
                if username in players:
                    past_x, past_y = players[username][0]

                    players[username][1] = ((current_x - past_x) // tickPerFrame, (current_y - past_y) // tickPerframe)

                    if sum(players[username][1]) < 3:
                        players[username][1] = (0, 0)
                        players[username][0] = [past_x, past_y]

                else:
                    players[username] = [[current_x, current_y], (0, 0)]

            elif command == 2:
                chunk_positionX, chunk_positionY, world_chunk = message

                world[chunk_positionX-5:chunk_positionX+45, chunk_positionY-5:chunk_positionY+31] = np.array(world_chunk, copy=True)

                if (chunk_positionX, chunk_positionY) in render_request:
                    render_request.remove((chunk_positionX, chunk_positionY))

            elif command == 3:
                pos_x, pos_y = message

                world[pos_x, pos_y] = 0

                if (pos_x, pos_y) in block_request:
                    block_request.remove((pos_x, pos_y))

            elif message == 4:
                pos_x, pos_y, block = message

                world[pos_x, pos_y] = block

                if (pos_x, pos_y) in block_request:
                    block_request.remove((pos_x, pos_y))

            elif message == 9:
                username = message[0]

                del players[username]

        except:
            pass

        #==================Render World==========================

        for x in range(0, 821, block_size):  # Render blocks
            for y in range(0, 521, block_size):
                block = world[(x + x_offset) // block_size][(y + y_offset) // block_size]

                if len(block_list) > block > 0:
                        screen.blit(block_texture[block], (x - x_offset % 20, y - y_offset % 20))

                elif block == -1:
                    draw.rect(screen, (0, 0, 0), (x - x_offset % 20, y - y_offset % 20, block_size, block_size))

        display.flip()
        clock.tick(60)

        '''
        to do list:
            Make world generation alg
            make the server command decoder
            do player interpolation
            get sprite
        '''

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5176

    navigation = 'menu'

    size = (800, 500)
    screen = display.set_mode(size)

    init()
    font.init()

    game(screen, "Ryan", host, port)

