import pickle
import socket
from multiprocessing import *
from collections import *
import numpy as np
from pygame import *
import os

#os.environ['SDL_VIDEO_WINDOW_POS'] = '1925,30'

sendQueue = Queue()
messageQueue = Queue()


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


def draw_block(x, y, size, colour, colourIn, screen):
    draw.rect(screen, colour, (x - x_offset % 20, y - y_offset % 20, block_size, block_size))
    draw.rect(screen, colourIn, (x - x_offset % 20, y - y_offset % 20, block_size, block_size), 1)

with open("config", "r") as config:
    config = config.read().split("\n")
    host = config[0]
    port = int(config[1])
    worldname = config[2]

if __name__ == '__main__':
    clock = time.Clock()

    # ----- Pre-Gameloop Preparation

    # Make the block size and block offset
    block_size = 20
    y_offset = 10 * block_size
    x_offset = 5000 * block_size

    display.set_caption("Random World Generator!")
    screen = display.set_mode((800, 500))

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Client connecting to %s:%i" % (host, port))

    server.sendto(pickle.dumps([0, 'Henry']), (host, port))

    sender = Process(target=playerSender, args=(sendQueue, server))
    sender.start()

    receiver = Process(target=receiveMessage, args=(messageQueue, server))
    receiver.start()

    Worldsize = messageQueue.get()

    world = np.array([[-1 for y in range(Worldsize[1])] for x in range(Worldsize[0])])

    updated = False

    sendQueue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])
    wmsg = messageQueue.get()
    world[wmsg[1]-5:wmsg[1]+45, wmsg[2]-5:wmsg[2]+31] = np.array(wmsg[3], copy=True)
    block_Select = 1

    # ----- Gameloop

    while True:
        updated = False
        for e in event.get():
            if e.type == QUIT:
                sender.terminate()
                receiver.terminate()
                break

            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4:
                    block_Select = min(3, block_Select + 1)

                elif e.button == 5:
                    block_Select = max(0, block_Select - 1)



        else:
            display.set_caption("Minecrap Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " X: " + str(x_offset // block_size) + " Y:" + str(y_offset // block_size) + " Size:" + str(block_size) + "Block Selected:" + str(block_Select))

            keys = key.get_pressed()

            if keys[K_d] and x_offset // block_size < 9950:
                x_offset += 60 // block_size
                updated = True
            elif keys[K_a] and x_offset // block_size > 0:
                x_offset -= 60 // block_size
                updated = True

            if keys[K_w] and y_offset // block_size > 5:
                y_offset -= 80 // block_size
                updated = True
            elif keys[K_s] and y_offset // block_size < 70:
                y_offset += 80 // block_size
                updated = True

            DispingWorld = world[x_offset // block_size:x_offset // block_size + 41, y_offset // block_size:y_offset // block_size + 26]
            updateCost = DispingWorld.flatten()
            updateCost = np.count_nonzero(updateCost == -1)

            if updated and updateCost > 3:

                sendQueue.put([[2, x_offset // block_size, y_offset // block_size], (host, port)])

            #screen.fill((0,0,255))

            try:
                wmsg = messageQueue.get_nowait()
                if wmsg[0] == 2:
                    world[wmsg[1]-5:wmsg[1] + 45, wmsg[2]-5:wmsg[2] + 31] = np.array(wmsg[3], copy=True)
                elif wmsg[0] == 3:
                    world[wmsg[1], wmsg[2]] = 0
                elif wmsg[0] == 4:
                    world[wmsg[1], wmsg[2]] = wmsg[3]
            except:
                pass

            mb = mouse.get_pressed()

            mx, my = mouse.get_pos()

            if mb[0] == 1:
                if world[(mx + x_offset) // block_size, (my + y_offset) // block_size] != 0:
                    sendQueue.put([[3, (mx + x_offset) // block_size, (my + y_offset) // block_size], (host, port)])
            if mb[2] == 1:
                if world[(mx + x_offset) // block_size, (my + y_offset) // block_size] == 0:
                    sendQueue.put([[4, (mx + x_offset) // block_size, (my + y_offset) // block_size, block_Select], (host, port)])


            #print((mx + x_offset) // block_size, (my + y_offset) // block_size)

            for y in range(500):
                draw.line(screen, (max(30 - y, 0), max(144 - y, 100), max(255 - y, 100)), (0, y), (800, y))

            # Clear the screen
            # Redraw the level onto the screen
            for x in range(0, 821, block_size):  # Render blocks
                for y in range(0, 521, block_size):
                    if world[(x + x_offset) // block_size][(y + y_offset) // block_size] == 1:
                        draw_block(x, y, block_size, (0, 150, 0), (0, 100, 0), screen)

                    elif world[(x + x_offset) // block_size][(y + y_offset) // block_size] == 2:
                        draw_block(x, y, block_size, (129, 68, 32), (99, 38, 12), screen)

                    elif world[(x + x_offset) // block_size][(y + y_offset) // block_size] == 3:
                        draw_block(x, y, block_size, (150, 150, 150), (100, 100, 100), screen)

            clock.tick(120)
            display.update()
            continue

        break

    display.quit()
    raise SystemExit
