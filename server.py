import os.path
import sys
from collections import deque
import socket
import pickle
from multiprocessing import *
from numpy import *
from world import *
import glob

# If world doesn't exist
if not os.path.isfile('world.pkl'):
    # Generate a new world with the function
    # world_seed,maxHeight,minX,maxX,w,h
    world = generate_world(input("Seed:\n"), 1, 3, 10, 10000, 100)

    # Dumps world to file
    with open('world.pkl', 'wb') as file:
        dump(world, file)

else:
    world = pickle.load(open('world.pkl', 'rb'))


class Player(object):
    global PlayerData, PlayerUUID, itemLib

    def __init__(self, player_number, player_username, x_offset, y_offset):
        self.username = player_username
        self.number = player_number

        self.cord, self.spawnCord, self.inventory, self.health, self.hunger = self.get_player_info()

        # self.saturation, self.foodLib

        if self.cord == (0, 0):
            self.cord = [x_offset, y_offset]

    def get_player_info(self):
        try:
            return PlayerData[self.username]
        except:
            PlayerData[self.username] = [(0, 0), (0, 0), [[0] * 2 for _ in range(36)], 10, 10]
            return PlayerData[self.username]

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

        pass

        self.inventory = [[0] * 2 for _ in range(36)]
        self.hunger = 10
        self.health = 10
        # self.saturation = 10

    def save(self):
        return [self.cord, self.spawnCord, self.inventory, self.health, self.hunger]


class World:
    def __init__(self, world_name):
        self.overworld = self.load_world(world_name)

    def load_world(self, worldn):
        return pickle.load(open(worldn + ".pkl", "rb"))

    def get_world(self, x, y):
        return self.overworld[x - 5:x + 45, y - 5:y + 31]

    def break_block(self, x, y):
        self.overworld[x, y] = 0

    def place_block(self, x, y, blocktype):
        self.overworld[x, y] = blocktype

    def save(self):
        pickle.dump(self.overworld, open('world.pkl', 'wb'))


def player_sender(send_queue, server):
    print('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    print('Server is ready for connection!')

    while True:
        try:
            message = server.recvfrom(1024)
        except:
            continue
        message_queue.put((pickle.loads(message[0]), message[1]))


def commandline_in(commandline_queue, fn):
    print('Ready for input.')
    sys.stdin = os.fdopen(fn)

    while True:
        command = input()
        commandline_queue.put(((10, command), ('127.0.0.1',)))


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

    with open("config", "r") as config:

        config = config.read().split("\n")
        host = config[0]
        port = int(config[1])
        world_name = config[2]

    world = World(world_name)

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Server binded to %s:%i" % (host, port))

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
        print(message)
        # print(message, address)
        command = message[0]

        if command == 0:
            # Create player/login
            # Data: [0,<username>,<x_offset>,<y_offset>]

            if message[1] not in username:

                if not playerNDisconnect:
                    PN = player_number
                    player_number += 1
                else:
                    PN = playerNDisconnect.popleft()

                players[address] = (Player(PN, message[1], message[2], message[3]), message[1])
                sendQueue.put(((10000, 100, players[address][0].cord[0], players[address][0].cord[1]), address))
                print('Player %s has connected from %s' % (message[1], address))
                username.add(message[1])

                for i in players:
                    if players[i][1] != players[address][1]:
                        sendQueue.put(
                            ((1, players[address][1], players[address][0].cord[0], players[address][0].cord[1]), i))

            else:
                sendQueue.put(((400,), address))

        elif command == 1:
            # Player movement
            # Data: [1, <cordx>, <cordy>]
            x, y = players[address][0].change_location((message[1], message[2]))

            for i in players:
                if players[i][1] != players[address][1]:
                    sendQueue.put(((1, players[address][1], x, y), i))

        elif command == 2:
            # Render world
            # Data: [2, <cordx>, <cordy>]
            sendQueue.put(((2, message[1], message[2], world.get_world(message[1], message[2])), address))

        elif command == 3:
            # Break block
            # Data: [3, <cordx>, <cordy>]
            world.break_block(message[1], message[2])

            for i in players:
                sendQueue.put(((3, message[1], message[2]), i))

        elif command == 4:
            # Place block
            # Data: [4, <cordx>, <cordy>, <block type>]
            world.place_block(message[1], message[2], message[3])

            for i in players:
                sendQueue.put(((4, message[1], message[2], message[3]), i))

        # elif command == 5:
        #     player[address][0].change_inventory

        elif command == 9:

            print('Player %s has disconnected from the game. %s' % (players[address][1], address))

            playerNDisconnect.append(players[address][0].number)
            PlayerData[players[address][1]] = players[address][0].save()
            offPlayer = players[address][1]
            username.remove(offPlayer)

            del players[address]

            for i in players:
                sendQueue.put(((9, offPlayer), i))

        elif command == 10:
            if message[1].lower() == "quit":
                receiver.terminate()
                sender.terminate()
                commandline.terminate()
                server.close()
                world.save()
                break

            if message[1].lower() == "del world":
                if input("<Rahmish Empire> CONFIRM: DELETE WORLD? THIS CHANGE IS PERMANENT (y/n) [n]: ").lower() == "y":
                    os.remove("world.pkl")
                    print("World deleted successfully\nServer will shutdown")
                    receiver.terminate()
                    sender.terminate()
                    commandline.terminate()
                    server.close()

                    break

                else:
                    print("Command aborted")

        elif command == 100:
            sendQueue.put(('hello', address))