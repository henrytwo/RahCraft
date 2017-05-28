import os.path
from collections import deque
import socket
import pickle as pkl
from multiprocessing import *

from subprocess import Popen, PIPE
from shlex import split
import platform
import numpy as np

from components.world import *
from math import *
import time
from random import *
import sys
import traceback

with open("data/config.rah", "r") as config:
    config = config.read().strip().split("\n")
    host = config[0]
    port = int(config[1])
    world_name = config[2]
    slack_enable = int(config[3])
    channel = config[4]
    online = int(config[5])

# If world doesn't exist
if not os.path.isfile('saves/%s.pkl' % world_name):
    # Generate a new world with the function
    # world_seed,maxHeight,minX,maxX,w,h
    world = generate_world(input("Seed:\n"), 1, 3, 10, 10000, 100)

    # Dumps world to file
    with open('saves/%s.pkl' % world_name, 'wb') as file:
        pkl.dump(world, file)

else:
    world = pkl.load(open('saves/world.pkl', 'rb'))


class Player(object):
    global PlayerData, PlayerUUID, itemLib

    def __init__(self, player_number, player_username):
        self.username = player_username
        self.number = player_number

        self.cord, self.spawnCord, self.inventory, self.hotbar, self.health, self.hunger = self.get_player_info()

        # self.saturation, self.foodLib

    def get_player_info(self):
        try:
            return PlayerData[self.username]
        except KeyError:
            PlayerData[self.username] = [world.spawnpoint, world.spawnpoint,
                                         [[[randint(0, 15), randint(0, 64)] for _ in range(9)] for __ in range(3)],
                                         [[randint(100, 102), 1] for _ in range(9)],
                                         10, 10]

            # print(PlayerData[self.username])
            return PlayerData[self.username]

    def change_spawn(self, spawn_position):
        self.spawnCord = spawn_position[:]

    def change_location(self, cord_change):
        self.cord = cord_change[:]

        return self.cord[0], self.cord[1]

    def change_inventory(self, item, slot, amount):
        self.inventory[slot][0] = self.itemLib[item]
        self.inventory[slot][1] += amount

        if self.inventory[slot][1] == 0:
            self.inventory[slot][0] = 0

    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.respawn()

    def update_food(self, food):
        # self.hunger += self.foodLib[food][0]
        # self.satura += self.foodLib[food][0]

        pass

    def respawn(self):
        # self.x = self.spawnx
        # self.y = self.spawny

        self.inventory = [[0, 0] for _ in range(36)]
        self.hotbar = [[0, 0] * 2 for _ in range(36)]
        self.hunger = 10
        self.health = 10
        # self.saturation = 10

    def save(self, block_size):
        return [(self.cord[0] // block_size, self.cord[1] // block_size), self.spawnCord, self.inventory, self.hotbar,
                self.health, self.hunger]


class World:
    def __init__(self, world_name):
        self.overworld = self.load_world(world_name)
        self.spawnpoint = self.get_spawnpoint()

    def load_world(self, worldn):
        return pkl.load(open("saves/" + worldn + ".pkl", "rb"))

    def get_world(self, x, y):
        return self.overworld[x - 5:x + 45, y - 5:y + 31]

    def break_block(self, x, y):
        self.overworld[x, y] = 0

    def place_block(self, x, y, blocktype):
        self.overworld[x, y] = blocktype

    def get_spawnpoint(self):
        x = len(self.overworld) // 2
        spawn_offset = 0
        spawn_found = False
        search_cords = self.overworld[x, :len(self.overworld[x]) // 2]

        while not spawn_found:
            for y in range(len(search_cords)):
                if y != 0 and search_cords[y] != 0:
                    spawn_found = True
                    x += spawn_offset
                    y -= 1
                    break

            if spawn_offset < 0:
                spawn_offset = abs(spawn_offset)
            elif spawn_offset > 0:
                spawn_offset = spawn_offset * -1 - 1
            else:
                spawn_offset -= 1

            search_cords = self.overworld[x + spawn_offset, :len(self.overworld[x + spawn_offset]) // 2]

        return x, y

    def save(self):
        pkl.dump(self.overworld, open('saves/world.pkl', 'wb'))


def player_sender(send_queue, server):
    print('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pkl.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    print('Server is ready for connection!')

    while True:
        try:
            message = server.recvfrom(1024)
        except:
            continue
        message_queue.put((pkl.loads(message[0]), message[1]))


def commandline_in(commandline_queue, fn):
    print('Ready for input.')
    sys.stdin = os.fdopen(fn)

    while True:
        command = input('[Server]>')
        commandline_queue.put(((10, command), ('127.0.0.1',)))


def heart_beats(message_queue, tick):
    while True:
        time.sleep(.06)
        tick += 1
        if tick % 1200 == 0:
            message_queue.put(((100, round(time.time(), 3), tick), ("127.0.0.1", 0000)))
            if tick >= 24000:
                tick = 1

def authenticate(message):
    global online

    if not online:
        return True

    user, token = message

    host, port = 'rahmish.com', 1111

    socket.setdefaulttimeout(10)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVERADDRESS = (host, port)
    socket.setdefaulttimeout(None)

    try:
        server.connect(SERVERADDRESS)
        server.send(pkl.dumps([2, [user, token]]))

        while True:

            first_message = pkl.loads(server.recv(4096))

            if first_message[0] == 1:
                server.close()
                return True

            else:
                server.close()
                return False
    except:
        server.close()
        return False



if __name__ == '__main__':
    players = {}
    player_number = 1

    playerNDisconnect = deque([])
    move = ''

    PlayerData = {}

    sendQueue = Queue()
    messageQueue = Queue()
    commandlineQueue = Queue()
    itemLib = {}
    username = set()

    if slack_enable:
        from components.slack import *
        config_slack()

    world = World(world_name)

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Server binded to %s:%i" % (host, port))

    heart_beat = Process(target=heart_beats, args=(messageQueue, 0))  # Change the tick stuff later
    heart_beat.start()

    receiver = Process(target=receive_message, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=player_sender, args=(sendQueue, server))
    sender.start()

    fn = sys.stdin.fileno()
    commandline = Process(target=commandline_in, args=(messageQueue, fn))
    commandline.start()
    cmdIn = ""

    while True:
        pickled_message = messageQueue.get()
        message, address = pickled_message
        command = message[0]

        if command == 0:
            # Player login and authentication
            # Data: [0,<username>, <token>]

            if message[1] not in username and authenticate(message[1:3]):

                if not playerNDisconnect:
                    PN = player_number
                    player_number += 1
                else:
                    PN = playerNDisconnect.popleft()

                playerLocations = {players[x].username: players[x].cord for x in players}

                players[address] = Player(PN, message[1])
                sendQueue.put(((0, 10000, 100, str(players[address].cord[0]), str(players[address].cord[1]),
                                players[address].hotbar, players[address].inventory, playerLocations), address))

                messageQueue.put(((10, "%s has connected to the game" % message[1]), ('127.0.0.1',)))
                #print('Player %s has connected from %s' % (message[1], address))
                username.add(message[1])

                for i in players:
                    if players[i].username != players[address].username:
                        sendQueue.put(((1, players[address].username, str(players[address].cord[0]),
                                        str(players[address].cord[1])), i))

            else:
                sendQueue.put(((400, (
                "\n\nConnection closed by remote host\nUsername in use or session\nis invalid (Try restarting the game)\n\n")), address))

        elif command == 1:
            # Player movement
            # Data: [1, <cordx>, <cordy>]
            x, y = players[address].change_location((message[1], message[2]))

            for i in players:
                if players[i].username != players[address].username:
                    sendQueue.put(((1, players[address].username, x, y), i))

        elif command == 2:
            # Render world
            # Data: [2, <cordx>, <cordy>]
            sendQueue.put(((2, message[1], message[2], world.get_world(message[1], message[2])), address))

        elif command == 3:
            # Break block
            # Data: [3, <cordx>, <cordy>]
            if hypot(world.spawnpoint[0] - message[1], world.spawnpoint[1] - message[2]) < 5:
                spawnpoint_check = world.get_spawnpoint()

                if spawnpoint_check != world.spawnpoint:
                    world.spawnpoint = spawnpoint_check[:]

                    for i in players:
                        players[i].change_spawn(world.spawnpoint)

            world.break_block(message[1], message[2])

            for i in players:
                sendQueue.put(((3, message[1], message[2]), i))

        elif command == 4:
            # Place block
            # Data: [4, <cordx>, <cordy>, <block type>]
            if hypot(world.spawnpoint[0] - message[1], world.spawnpoint[1] - message[2]) < 5:
                spawnpoint_check = world.get_spawnpoint()

                if spawnpoint_check != world.spawnpoint:
                    world.spawnpoint = spawnpoint_check[:]

                    for i in players:
                        players[i].change_spawn(world.spawnpoint)

            world.place_block(message[1], message[2], message[3])
            players[address].hotbar[message[4]][1] -= 1

            if players[address].hotbar[message[4]][1] == 0:
                players[address].hotbar[message[4]] = [0, 0]

            sendQueue.put(((6, message[4], players[address].hotbar[message[4]]), address))

            for i in players:
                sendQueue.put(((4, message[1], message[2], message[3]), i))

                # elif command == 5:
                # player[address][0].change_inventory()

        elif command == 9:

            messageQueue.put(((10, "%s has disconnected from the game"%players[address].username), ('127.0.0.1',)))
            #print('Player %s has disconnected from the game. %s' % (players[address].username, address))

            playerNDisconnect.append(players[address].number)
            PlayerData[players[address].username] = players[address].save(message[1])
            offPlayer = players[address].username
            username.remove(offPlayer)

            del players[address]

            for i in players:
                sendQueue.put(((9, offPlayer), i))

        elif command == 10:
            if message[1].lower() == "/quit":
                receiver.terminate()
                sender.terminate()
                commandline.terminate()
                heart_beat.terminate()
                server.close()
                world.save()
                break

            if message[1].lower() == "/del world":
                send_message = "<Rahmish Empire> CONFIRM: DELETE WORLD? THIS CHANGE IS PERMANENT (y/n) [n]: "

                sys.stdout.flush()
                in_put = messageQueue.get()
                while in_put[0][0] != 10:
                    # print(in_put)
                    in_put = messageQueue.get()

                if in_put[0][1] == 'y':
                    os.remove("saves/world.pkl")
                    send_message = "World deleted successfully\nServer will shutdown"
                    receiver.terminate()
                    sender.terminate()
                    commandline.terminate()
                    server.close()

                    exit()

                    break

                else:
                    send_message = "Command aborted"

            elif message[1].lower() == '/ping':
                send_message = 'pong!'

            elif message[1].lower() == '/lenin':
                with open('data/communist.rah') as communist:
                    for line in communist.read().split('\n'):
                        send_message = '[Comrade Lenin] ' + line

                        for i in players:
                            sendQueue.put(((10, send_message), i))

            elif message[1].lower()[:4] == '/say':
                send_message =  message[1][4:]

            elif message[1].lower()[:5] == '/exec':

                try:
                    exec(message[1][6:])
                    send_message = "Command '%s' executed by %s" % (message[1][6:], players[address].username)
                except:
                    send_message = "Command '%s' failed to execute: %s" % (message[1][6:], traceback.format_exc().replace('\n',''))

            elif message[1].lower()[:5] == '/bash':

                try:
                    print(Popen(split(message[1][6:]), stdout=PIPE))
                    send_message = "Bash command '%s' executed by %s" % (message[1][6:], players[address].username)
                except:
                    send_message = "Bash command '%s' failed to execute: %s" % (message[1][6:], traceback.format_exc().replace('\n',''))


            else:
                if address in players:
                    user_sending = players[address].username
                else:
                    user_sending = 'Server'

                send_message = '[%s] %s' % (user_sending, message[1])

            if send_message[0] != '[':
                send_message = '[Server] ' + send_message

            for i in players:
                sendQueue.put(((10, send_message), i))

            if slack_enable:
                broadcast(channel, send_message)

        elif command == 100:
            for p in players:
                sendQueue.put((message, p))
            broadcast(channel, '[Tick] %s'%message[2])
