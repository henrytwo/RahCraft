from pygame import *
import pickle
import socket
from threading import *
from multiprocessing import *
import sys
from numpy import *

sendQueue = Queue()

def playerSender(sendQueue, server):
    print('Client running...')

    while True:
        tobesent = sendQueue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def draw_block(x, y, size, colour, colourIn, screen):
    draw.rect(screen, colour, (x, y, block_size, block_size))
    draw.rect(screen, colourIn, (x, y, block_size, block_size), 1)


# Create the game screen


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
    y_offset = 0
    x_offset = 0

    display.set_caption("Random World Generator!")
    screen = display.set_mode((800, 500))

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Server binded to %s:%i" % (host, port))

    server.sendto(pickle.dumps([0, 'Henry']), (host, port))

    # Generate a new world with the function

    sender = Process(target=playerSender, args=(sendQueue, server))
    sender.start()
    updated = False

    sendQueue.put([[2, x_offset // block_size + 20, y_offset // block_size + 20], ('127.0.0.1', 5175)])
    world = pickle.loads(server.recvfrom(8192)[0])

    # ----- Gameloop

    while True:
        updated = False
        for e in event.get():
            if e.type == QUIT:
                break

            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4:
                    block_size += 4

                elif e.button == 5:
                    block_size -= 4



        else:
            display.set_caption("Minecrap Beta v0.01 FPS: " + str(round(clock.get_fps(), 2)) + " X: " + str(x_offset // block_size) + " Y:" + str(y_offset // block_size) + " Size:" + str(block_size))

            keys = key.get_pressed()
S
            if keys[K_d]:
                x_offset += 80 // block_size
                updated = True
            if keys[K_a]:
                x_offset -= 80 // block_size
                updated = True

            if keys[K_w]:
                y_offset -= 80 // block_size
                updated = True
            if keys[K_s]:
                y_offset += 80 // block_size
                updated = True

            if updated:
                sendQueue.put([[2, x_offset // block_size + 20, y_offset // block_size + 20], ('127.0.0.1', 5175)])
                world = pickle.loads(server.recvfrom(8192)[0])

            mb = mouse.get_pressed()

            mx, my = mouse.get_pos()

            screen.fill((30, 144, 255))

            # Clear the screen
            # Redraw the level onto the screen
            for x in range(len(world)):  # Render blocks
                for y in range(len(world[0])):
                    if world[x][y] == 1:
                        draw_block(x*block_size, y*block_size, block_size, (0, 150, 0), (0, 100, 0), screen)

                    elif world[x][y] == 2:
                        draw_block(x*block_size, y*block_size, block_size, (129, 68, 32), (99, 38, 12),  screen)

                    elif world[x][y] == 3:
                        draw_block(x*block_size, y*block_size, block_size, (150, 150, 150), (100, 100, 100),  screen)

            clock.tick()
            display.update()
            continue

        break

    display.quit()
    raise SystemExit