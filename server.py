import socket
from multiprocessing import *
from collections import deque
from numpy import *
import pickle
import glob
from world import *
import os.path
import sys

#If world doesn't exist
if not os.path.isfile('world.pkl'):
    # Generate a new world with the function
    world = generate_world(input("Seed:\n"), 1, 3, 10, 10000, 100)

    #Dumps world to file
    with open('world.pkl', 'wb') as file:
        dump(world, file)

else:
    world = pickle.load(open('world.pkl', 'rb'))



class Player(object):
    global PlayerData, PlayerUUID, itemLib

    def __init__(self, PlayerNumber, PlayerUsername, xOffset, yOffset):
        self.username = PlayerUsername
        self.number = PlayerNumber

        self.cord, self.spawnCord, self.inventory, self.health, self.hunger = self.get_playerInfo()

        if self.cord == (0, 0):
            self.cord = [xOffset, yOffset]

    def get_playerInfo(self):
        try:
            return PlayerData[self.username]
        except:
            PlayerData[self.username] = [(0, 0), (0, 0), [[0] * 2 for _ in range(36)], 10, 10]
            return PlayerData[self.username]

    def changeLocation(self, cordChange):
        self.cord = cordChange[:]

        return self.cord[0], self.cord[1]

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

        self.inventory = [[0] * 2 for _ in range(36)]
        self.hunger = 10
        self.health = 10
        self.satura = 10

    def save(self):
        self.PlayerData[self.username] = [(self.x, self.y), self.inventory, self.health, self.hunger]


class World:
    def __init__(self, worldname):
        self.overworld = self.loadworld(worldname)

    def loadworld(self, worldn):
        return pickle.load(open(worldn+".pkl","rb"))

    def getworld(self, x, y):
        return self.overworld[x-5:x+45, y-5:y+31]

    def breakblock(self, x, y):
        self.overworld[x, y] = 0

    def placeblock(self, x, y, blocktype):
        self.overworld[x, y] = blocktype

    def save(self):
        pickle.dump(self.overworld, open('world.pkl', 'wb'))


def playerSender(sendQueue, server):
    print('Sender running...')

    while True:
        tobesent = sendQueue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receiveMessage(messageQueue, server):
    print('Server is ready for connection!')

    while True:
        try:
            msg = server.recvfrom(1024)
        except:
            continue
        messageQueue.put((pickle.loads(msg[0]),msg[1]))


def commandlineIn(commandlineQueue, fn):
    print('Ready for input.')
    sys.stdin = os.fdopen(fn)

    while True:
        command = input()
        commandlineQueue.put(((10, command), ('127.0.0.1',)))


if __name__ == '__main__':
    players = {}
    playernumber = 1

    playerNDisconnect = deque([])
    move = ''

    PlayerData = {}
    PlayerUUID = {}

    sendQueue = Queue()
    messageQueue = Queue()
    commandlineQueue = Queue()
    itemLib = {}
    username = set()

    with open("config","r") as config:

        config = config.read().split("\n")
        host = config[0]
        port = int(config[1])
        worldname = config[2]

    world = World(worldname)

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Server binded to %s:%i"%(host,port))

    receiver = Process(target=receiveMessage, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=playerSender, args=(sendQueue,server))
    sender.start()

    fn = sys.stdin.fileno()
    commandline = Process(target=commandlineIn, args=(messageQueue, fn))
    commandline.start()
    cmdIn = ""

    while True:

        pickledmessage = messageQueue.get()
        message, address = pickledmessage
        #print(message, address)
        command = message[0]

        if command == 0:
            # Create player/login
            # Data: [0,<username>,<x_offset>,<y_offset>]

            if message[1] not in username:

                if not playerNDisconnect:
                    PN = playernumber
                    playernumber += 1
                else:
                    PN = playerNDisconnect.popleft()

                playerLocations = {players[x][0].username: [players[x][0].cord, (0, 0)] for x in players}

                players[address] = (Player(PN, message[1], message[2], message[3]), message[1])
                sendQueue.put(((0, 10000, 100, players[address][0].cord[0], players[address][0].cord[1], playerLocations), address))
                print('Player %s has connected from %s' % (message[1], address))
                username.add(message[1])

                for i in players:
                    if players[i][1] != players[address][1]:
                        sendQueue.put(((1, players[address][1], players[address][0].cord[0], players[address][0].cord[1]), i))

            else:
                sendQueue.put(((400,), address))


        elif command == 1:
            # Player movement
            # Data: [1, <cordx>, <cordy>]
            x, y = players[address][0].changeLocation((message[1], message[2]))

            for i in players:
                if players[i][1] != players[address][1]:
                    sendQueue.put(((1, players[address][1], x, y), i))

        elif command == 2:
            # Render world
            # Data: [2, <cordx>, <cordy>]
            sendQueue.put(((2, message[1], message[2], world.getworld(message[1], message[2])), address))

        elif command == 3:
            # Break block
            # Data: [3, <cordx>, <cordy>]
            world.breakblock(message[1], message[2])

            for i in players:
                sendQueue.put(((3, message[1], message[2]), i))

        elif command == 4:
            # Place block
            # Data: [4, <cordx>, <cordy>, <block type>]
            world.placeblock(message[1], message[2], message[3])

            for i in players:
                sendQueue.put(((4, message[1], message[2], message[3]), i))

        elif command == 5:
            player[address][0].changeInventory

        elif command == 10:
            if message[1].lower() == "quit":
                receiver.terminate()
                sender.terminate()
                commandline.terminate()
                server.close()
                world.save()
                break

        elif command == 100:

            sendQueue.put(('helo',address))
