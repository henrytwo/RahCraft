import socket
import uuid
from multiprocessing import *
from collections import deque
from numpy import *
import pickle
import glob
from generation import *
import os.path

players = {}
playernumber = 1

playerNDisconnect = deque([])
move = ''

PlayerData = {}
PlayerUUID = {}

sendQueue = Queue()
messageQueue = Queue()
itemLib = {}

# If world doesn't exist
if not os.path.isfile('world.pkl'):
    # Generate a new world with the function
    world = generate_world(input("Seed:\n"), 1, 3, 10, 10000, 100)

    # Dumps world to file
    with open('world.pkl', 'wb') as file:
        dump(world, file)

else:
    world = pickle.load(open('world.pkl', 'rb'))


class Player(object):
    global PlayerData, PlayerUUID, itemLib

    def __init__(self, PlayerNumber, PlayerUsername):
        self.username = PlayerUsername
        self.UUID = self.get_UUID()
        self.number = PlayerNumber

        self.cord, self.spawnCord, self.inventory, self.health, self.hunger, self.satura = self.get_playerInfo()

    def get_UUID(self):
        try:
            return PlayerUUID[self.username]
        except:
            PlayerUUID[self.username] = uuid.uuid1()
            return PlayerUUID[self.username]

    def get_playerInfo(self):
        try:
            return PlayerData[self.UUID]
        except:
            PlayerData[self.UUID] = [(0, 0), (0, 0), [[0] * 2 for _ in range(36)], 10, 10, 10]
            return PlayerData[self.UUID]

    def changeLocation(self, cordx):
        self.cord = cordx[:]

    def changeInventory(self, item, slot, amount):
        self.inventory[slot][0] = self.itemLib[item]
        self.inventory[slot][1] += amount

        if self.inventory[slot][1] == 0:
            self.inventory[slot][0] = 0

    def takeDamage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.respawn()

    def UpdateFood(self, food):
        self.hunger += self.foodLib[food][0]
        self.satura += self.foodLib[food][0]

    def respawn(self):
        self.x = self.spawnx
        self.y = self.spawny

        self.inventory = [[0] * 2] * 36
        self.hunger = 10
        self.health = 10
        self.satura = 10

    def save(self):
        self.PlayerData[self.UUID] = [(self.x, self.y), self.inventory, self.health, self.hunger, self.satura]


class World:
    def __init__(self, worldname):
        self.overworld = self.loadworld(worldname)

    def loadworld(self, worldn):
        return pickle.load(open(worldn + ".pkl", "rb"))

    def getworld(self, x, y):
        return self.overworld[x:x + 41, y:y + 27]

    def breakblock(self, x, y):
        self.overworld[x, y] = 0

    def placeblock(self, x, y, blocktype):
        self.overworld[x, y] = blocktype


def playerSender(sendQueue, server):
    print('Sender running...')

    while True:
        tobesent = sendQueue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def recieveMessage(messageQueue, server):
    print('Server is ready for connection!')

    while True:
        msg = server.recvfrom(1024)
        messageQueue.put((pickle.loads(msg[0]), msg[1]))


if __name__ == '__main__':

    with open("config", "r") as config:

        config = config.read().split("\n")
        host = config[0]
        port = int(config[1])
        worldname = config[2]

    world = World(worldname)

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Server binded to %s:%i" % (host, port))

    reciever = Process(target=recieveMessage, args=(messageQueue, server))
    reciever.start()

    sender = Process(target=playerSender, args=(sendQueue, server))
    sender.start()

    while True:
        pickledmessage = messageQueue.get()
        message, address = pickledmessage
        command = message[0]

        if command == 0:
            # Create player/login
            # Data: [0,<username>]

            if not playerNDisconnect:
                PN = playernumber
                playernumber += 1
            else:
                PN = playerNDisconnect.popleft()

            players[address] = (Player(PN, message[0]), message[1])
            sendQueue.put(((10000, 100), address))
            print('Connection established!')

        elif command == 1:
            # Player movement
            # Data: [1, <cordx>, <cordy>]
            players[address][0].changeLocation((message[1], message[2]))

        elif command == 2:
            # Render world
            # Data: [2, <cordx>, <cordy>]
            sendQueue.put(((message[1], message[2], world.getworld(message[1], message[2])), address))

        elif command == 3:
            # Break block
            # Data: [3, <cordx>, <cordy>]
            world.breakblock(message[1], message[2])

            for i in player:
                sendQueue.put((message, i))

        elif command == 4:
            # Place block
            # Data: [4, <cordx>, <cordy>]
            world.placeblock(message[1], message[2], message[3])

            for i in players:
                sendQueue.put((message, i))

        elif command == 5:
            player[address][0].changeInventory

        elif command == 100:

            sendQueue.put(('helo', address))

    reciever.terminate()
