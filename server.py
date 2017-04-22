import socket
import uuid
from threading import *
from multiprocessing import *
from collections import deque
from numpy import *
import pickle
import glob

players = {}
playernumber = 1

playerNDisconnect = deque([])
move = ''

PlayerData = {}
PlayerUUID = {}

sendQueue = Queue()
messageQueue = Queue()
itemLib = {}
'''
while True:
    command = input("Do you want to create a new world?[Y/N]:").lower()
    #generate_world(world_seed, maxHeight, minX, maxX, w, h)
    #world = generate_world(input("Seed:\n"), 1, 3, 10, 10000, 100)
    if command == 'y':
        seed = input("Enter a seed[Don't enter a seed to randomize]: ")
        try:
            height = int(input("Enter the max world height[Default]: "))
'''

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
            PlayerData[self.UUID] = [(0,0), (0,0), [[0] * 2 for _ in range(36)], 10, 10, 10]
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
'''
class World:
    def __init__(self):
        self.overworld = self.loadworld()

    def getworld(self, x, y):
        return self.overworld[x-10:x+10, y-10,y+10]

    def breakblock(self, x, y):
        self.overworld[x, y] = 0

    def placeblock(self, x, y, blocktype):
        slef.overworld[x, y] = blocktype
'''
def playerSender(sendQueue, server):
    print('Sender running...')

    while True:
        tobesent = sendQueue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def recieveMessage(messageQueue, server):
    print('Server is ready for connection!')

    while True:
        msg = server.recvfrom(1024)
        messageQueue.put((pickle.loads(msg[0]),msg[1]))
        print(messageQueue)


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 4909

    #world = World()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    reciever = Process(target=recieveMessage, args=(messageQueue, server))
    reciever.start()

    sender = Process(target=playerSender, args=(sendQueue,server))
    sender.start()

    while True:
        pickledmessage = messageQueue.get()
        message, address = pickledmessage
        print(message, address)
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
            print('Connection established!')

        elif command == 1:
            # Player movement
            # Data: [1, <cordx>, <cordy>]
            players[address][0].changeLocation((message[1], message[2]))
            print(address, message[1], message[2])

        elif command == 2:
            # Render world
            # Data: [2, <cordx>, <cordy>]
            sendQueue.put((world.getworld(message[1],message[2]), address))

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

            for i in player:
                sendQueue.put((message, i))

        elif command == 5:
            player[address][0].changeInventory

        elif command == 100:

            sendQueue.put(('helo',address))



    reciever.terminate()


