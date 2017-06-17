import os.path, sys, traceback, socket, json, platform, time, datetime

from collections import deque
import pickle as pkl
from multiprocessing import *
from copy import deepcopy
from subprocess import Popen, PIPE
from shlex import split
import numpy as np
from math import *
from random import *
import time as t
from components.slack import *
from components.world import *

import getpass
import requests


with open("data/config.rah", "r") as config: # Reading server settings from a file so that the settings can be easily modifiable and is saved
    config = config.read().strip().split("\n")
    host = config[0]  # The ip address that the socket will bind to
    port = int(config[1])  # The port that the socket will bind to
    world_name = config[2]  # The name of the world to load
    slack_enable = int(config[3])  # Slack integration to help with server management
    channel = config[4]  # Slack channel to broadcast messages
    online = int(config[5])  # Whether to check login with the auto server or not to prevent cheating
    whitelist_enable = int(config[6])  # Whitelist to control who can access the server


# If world doesn't exist
if not os.path.isfile('saves/%s.pkl' % world_name):
    # Generate a new world with the function
    # world_seed,maxHeight,minX,maxX,w,h
    world = generate_world(input("Seed:\n"), 30, 100, 10000, 100)

    # Dumps world to file
    with open('saves/%s.pkl' % world_name, 'wb') as file:
        pkl.dump(world, file)


# A player class is used here to store all of the important information about a player
# Functions are there to provide an easier way to modify player information
class Player(object):
    global PlayerData  # Global variable is user here to help with saving player data

    def __init__(self, player_number, player_username):  # Init function takes in the player number and the username for player lookup
        self.username = player_username
        self.number = player_number

        self.cord, self.spawnCord, self.inventory, self.hotbar, self.health, self.hunger = self.get_player_info()  # Getting the the player information using the get_player_info function

    # This function checks if the player has a save available. If there is, the saved data is returned. If player is not in PlayerData, then create a new save file for the player
    def get_player_info(self):
        if self.username in PlayerData:
            return PlayerData[self.username]
        else:
            PlayerData[self.username] = [world.spawnpoint, world.spawnpoint, [[[0, 0] for _ in range(9)] for __ in range(3)], [[0, 0] for _ in range(9)], 20, 20]

            return PlayerData[self.username]

    # Change the spawn point of the player due to griefing
    def change_spawn(self, spawn_position):
        self.spawnCord = spawn_position[:]

    # Modify the current position of the player to match the positions that the client sent for saving
    def change_location(self, cord_change):
        self.cord = cord_change[:]

        rahprint(self.cord)  # rahprint function for debugging

        return self.cord[0], self.cord[1]

    # Change the complete inventory and the hotbar of the player
    def change_inventory_all(self, cinventory, chotbar):
        self.inventory = deepcopy(cinventory)
        self.hotbar = deepcopy(chotbar)

    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.respawn()

    # Returns player data for saving
    def save(self):
        return [(self.cord[0], self.cord[1]), self.spawnCord, self.inventory, self.hotbar,
                self.health, self.hunger]

# The world class contains the numpy array of the world and several useful function for easier modification of the world
class World:
    def __init__(self, world_name):  # Uses the world name to load the world from the saves
        self.overworld = pkl.load(open("saves/" + worldn + ".pkl", "rb"))
        self.spawnpoint = self.get_spawnpoint()

    def get_world(self, x, y, size, block_size):  # Function to calculate the what blocks to send to the client

        width, height = size[0] // block_size, size[1] // block_size

        return self.overworld[x - 5:x + width + 5, y - 5:y + height + 5]

    def break_block(self, x, y):  # A block is broken so the numpy array needs to be modified
        self.overworld[x, y] = 0

    def place_block(self, x, y, blocktype):  # A block is placed so the numpy array needs to be modified
        self.overworld[x, y] = blocktype

    def get_spawnpoint(self):  # This function calculates the spawn point of the world
        x = len(self.overworld) // 2  # The search begans in the middle of the world and spreads out from there
        spawn_offset = 0
        spawn_found = False
        search_cords = self.overworld[x, :len(self.overworld[x])]  # A list of cords to search

        while not spawn_found:  # While a vaild spawnpoint is not found
            for y in range(len(search_cords)):
                if y != 0 and search_cords[y] != 0:  # if the spawnpoint is found
                    spawn_found = True  # Setting spawn_found to true to break the search while loop
                    x += spawn_offset  # getting the offset + the starting x
                    y -= 1  # getting the currect y cord
                    break

            if spawn_offset < 0:  # These if statements reverses the spawn_offset every loop to search once on the left and once on the right.
                spawn_offset = abs(spawn_offset)
            elif spawn_offset > 0:
                spawn_offset = spawn_offset * -1 - 1
            else:
                spawn_offset -= 1  # Increase/decrease the offset to increase search range

            search_cords = self.overworld[x + spawn_offset, :len(self.overworld[x + spawn_offset])]  # Getting the cords needed to be searched on the next loop

        return x, y

    def save(self):  # Saving the world to a file
        pkl.dump(self.overworld, open('saves/world.pkl', 'wb'))

# A function used to write the server log to a file to help with server debugging
def logger(log_queue):
    with open('data/log.log', 'a+') as data_file:
        while True:
            data_file.write(str(log_queue.get()) + '\n')
            data_file.flush()  # Flushing the data so it can be written to the os write queue and be written to the file without calling close

# A useful function for debugging. Print_enable can disable debug printing with ease
def rahprint(text):
    print_enable = False

    if print_enable:
        print(text)

# A sender that sends the messages to the clients using socket io
def player_sender(send_queue, server):
    rahprint('Sender running...')

    while True:
        tobesent = send_queue.get() # This gets the message needed to be sent from a queue
        try:  # A try except is used here because socket will return an error if the destination address is not valid
            server.sendto(pkl.dumps(tobesent[0], protocol=4), tobesent[1])  # Pickles the message to bytes and sends to the address
        except:
            print(tobesent[0])

# A message reciever is used to prevent loss of messages due to socket overload/socket buffer is full
def receive_message(message_queue, server):
    rahprint('Server is ready for connection!')
    while True:
        try:  # A try except is needed here because the server can sometimes recieve partial packet due to client crash or internet error
            message = server.recvfrom(1024)  # Recieving messages with a buffer of 1024 bits
            message_queue.put((pkl.loads(message[0]), message[1]))  # Puts both the message and the address into the message queue because UDP is a connectionless protocol. The only way to identify a client is by address
        except:
            continue

# Give items is a function used by the /give command
# This function helps find a space to put the item
def give_item(inventory, hotbar, Nitem, quantity):
    item_location = ''  # used to store the first location where the item can be stored
    inventory_type = ''  # This is used to store the first open slot type (inventory or hotbar)
    for item in range(len(hotbar)):  # Loop through the hotbar first because the hotbar takes priority
        if hotbar[item][1] < 64:  # If stacking is possible, stack item and quit
            hotbar[item][1] += quantity
            return inventory, hotbar
        elif hotbar[item][0] == 0 and inventory_type == '':  # If an open space is found, store the cords and type for later use if not valid stacking spot is found
            item_location = item
            inventory_type = 'hotbar'

    for row in range(len(inventory)):  # Same as above but searches through the inventory instead
        for item in range(len(inventory[row])):
            if inventory[row][item][0] == Nitem and inventory[row][item][1] < 64:
                inventory[row][item][1] += quantity
                return inventory, hotbar
            elif inventory[row][item][0] == 0 and inventory_type == '':
                item_location = [row, item]
                inventory_type = 'inventory'

    if inventory_type == 'hotbar':  # If no place to stack te inventory is found, place the item(s) in the first open slot found
        hotbar[item_location] = [Nitem, quantity]
    elif inventory_type == 'inventory':
        inventory[item_location[0]][item_location[1]] = [Nitem, quantity]

    return inventory, hotbar


def commandline_in(commandline_queue, fn):
    rahprint('Ready for input.')
    sys.stdin = os.fdopen(fn)

    while True:
        command = input('> ')
        commandline_queue.put(((10, command), ('127.0.0.1', 0000)))


def heart_beats(message_queue, global_tick, tick):
    while True:
        time.sleep(.06)
        tick += 1
        global_tick.value += 1
        if tick % 100 == 0:
            message_queue.put(((100, round(time.time(), 3), tick), ("127.0.0.1", 0000)))
            if tick >= 24000:
                tick = 1

def collect_system_info():

    sys_information = [
                  platform.machine(),
                  platform.version(),
                  platform.platform(),
                  platform.uname(),
                  platform.system(),
                  platform.processor(),
                  getpass.getuser(),
                  datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S'),
                  requests.get('http://ip.42.pl/raw').text]

    return sys_information

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
        server.send(pkl.dumps([2, [user, token, collect_system_info()]]))

        while True:

            first_message = pkl.loads(server.recv(10096))

            if first_message[0] == 1:
                server.close()
                return True

            else:
                server.close()
                return False
    except:
        server.close()
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    players = {}
    username_dict = {('127.0.0.1', 0):'Rahbot'}
    player_number = 1

    active_players = []

    playerNDisconnect = deque([])
    move = ''

    PlayerData = {}

    sendQueue = Queue()
    messageQueue = Queue()
    commandlineQueue = Queue()
    log_queue = Queue()

    itemLib = {}
    global_tick = Value('l', 0)
    username = set()

    if slack_enable:
        config_slack()

    world = World(world_name)

    chests = {}
    furnaces = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    rahprint("Server binded to %s:%i" % (host, port))

    log_process = Process(target=logger, args=(log_queue,))
    log_process.start()

    heart_beat = Process(target=heart_beats, args=(messageQueue, global_tick, 0))  # Change the tick stuff later
    heart_beat.start()

    receiver = Process(target=receive_message, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=player_sender, args=(sendQueue, server))
    sender.start()

    fn = sys.stdin.fileno()
    commandline = Process(target=commandline_in, args=(messageQueue, fn))
    commandline.start()
    cmdIn = ""

    with open('data/motd.rah') as motd:
        motd = choice(motd.read().strip().split('\n'))

    with open('data/whitelist.rah') as whitelist:
        whitelist = whitelist.read().strip().split('\n')

    with open('data/op.rah') as op:
        op = op.read().strip().split('\n')

    with open('data/op_config.rah') as op_commands:
        op_commands = op_commands.read().strip().split('\n')

    with open('data/ban.json') as ban_file:
        ban = json.load(ban_file)


    while True:
        pickled_message = messageQueue.get()
        message, address = pickled_message
        command = message[0]

        try:

            # External commands
            if command == 0:
                # Player login and authentication
                # Data: [0,<username>, <token>]

                if message[1] not in ban:

                    if whitelist_enable and message[1] in whitelist or not whitelist_enable:

                        if message[1] not in username:

                            if authenticate(message[1:3]):

                                if not playerNDisconnect:
                                    PN = player_number
                                    player_number += 1
                                else:
                                    PN = playerNDisconnect.popleft()

                                playerLocations = {players[x].username: players[x].cord for x in players}

                                players[address] = Player(PN, message[1])
                                username_dict[address] = message[1]

                                sendQueue.put(((0, 10000, 100, players[address].cord[0], players[address].cord[1], players[address].hotbar, players[address].inventory, playerLocations, players[address].health, players[address].hunger ), address))

                                active_players.append(address)

                                messageQueue.put(((10, "%s has connected to the game" % message[1]), ('127.0.0.1', 0000)))
                                # rahprint('Player %s has connected from %s' % (message[1], address))
                                username.add(message[1])

                                for i in players:
                                    if players[i].username != username_dict[address]:
                                        sendQueue.put(((1, username_dict[address], players[address].cord[0], players[address].cord[1], False), i))

                            else:
                                sendQueue.put(((400, (
                                    "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\nCredentials were rejected by\nRahCraft Authentication Service\n(Try logging in again)\n\n")),
                                               address))

                        else:
                            sendQueue.put(((400, (
                                "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\nUsername currently in use\nIf you recently disconnected,\ntry to login again")),
                                           address))

                    else:
                        sendQueue.put(((400, (
                            "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\nThis server is white listed\nIf you believe this is an error,\nContact the administrator for assistance")),
                                       address))
                else:
                    sendQueue.put(((400, (
                        "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\n%s" % ban[message[1]]['message'])),
                                   address))

            # External heartbeat
            elif command == 102:
                sendQueue.put(((102, motd, host, port), address))

            elif address in players or address == ('127.0.0.1', 0000):
                if command == 1:

                    # Player movement
                    # Data: [1, <cordx>, <cordy>]
                    x, y = players[address].change_location((message[1], message[2]))

                    for i in players:
                        sendQueue.put(((1, username_dict[address], x, y, False), i))

                elif command == 2:
                    # Render world
                    # Data: [2, <cordx>, <cordy>, <size>]
                    sendQueue.put(((2, message[1], message[2], world.get_world(message[1], message[2], message[3], message[4])), address))

                elif command == 3:
                    # Break block
                    # Data: [3, <cordx>, <cordy>]
                    if hypot(world.spawnpoint[0] - message[1], world.spawnpoint[1] - message[2]) < 2:
                        spawnpoint_check = world.get_spawnpoint()

                        if spawnpoint_check != world.spawnpoint:
                            world.spawnpoint = spawnpoint_check[:]

                            for i in players:
                                players[i].change_spawn(world.spawnpoint)

                    if world.overworld[message[1], message[2]] == 17 and [message[1], message[2]] in chests:
                        del chests[[message[1], message[2]]]

                    world.break_block(message[1], message[2])

                    for i in players:
                        sendQueue.put(((3, message[1], message[2]), i))

                elif command == 4:
                    # Place block
                    # Data: [4, <cordx>, <cordy>, <block type>]
                    if hypot(world.spawnpoint[0] - message[1], world.spawnpoint[1] - message[2]) < 2:
                        spawnpoint_check = world.get_spawnpoint()

                        if spawnpoint_check != world.spawnpoint:
                            world.spawnpoint = spawnpoint_check[:]

                            for i in players:
                                players[i].change_spawn(world.spawnpoint)

                    world.place_block(message[1], message[2], message[3])
                    players[address].hotbar[message[4]][1] -= 1

                    if players[address].hotbar[message[4]][1] <= 0 or players[address].hotbar[message[4]][0] == 0:
                        players[address].hotbar[message[4]] = [0, 0]

                    sendQueue.put(((6, message[4], players[address].hotbar[message[4]]), address))
                    if message[3] == 17:
                        chests[(message[1], message[2])] = [[[[0, 0] for _ in range(9)] for __ in range(3)], [address[:]]]
                    elif message[3] == 18:
                        furnaces[(message[1], message[2])] = [[[0, 0], [0, 0], [0, 0]], [address[:]]]

                    for i in players:
                        sendQueue.put(((4, message[1], message[2], message[3]), i))

                elif command == 5:
                    players[address].change_inventory_all(message[1], message[2])

                elif command == 7:
                    if message[1] == 'chest':
                        if message[-1] == 1:
                            try:
                                chests[(message[2], message[3])][1].append(address)
                                sendQueue.put(([8, 'chest', chests[message[2], message[3]][0]], address))
                            except:
                                sendQueue.put(([8, "err"], address))
                        else:
                            try:
                                chests[(message[2], message[3])][1].remove(address)
                            except:
                                sendQueue.put(([8, "err"], address))

                    elif message[1] == 'furnace':
                        if message[-1] == 1:
                            try:
                                furnaces[(message[2], message[3])][1].append(address)
                                sendQueue.put(([8, 'furnace', furnaces[message[2], message[3]][0]], address))
                            except:
                                print(traceback.format_exc())
                                sendQueue.put(([8, "err"], address))
                        else:
                            try:
                                furnaces[(message[2], message[3])][1].remove(address)
                            except:
                                print(traceback.format_exc())
                                sendQueue.put(([8, "err"], address))

                elif command == 8:
                    print(pickled_message)
                    if message[1] == 'chest':
                        if chests[(message[5], message[6])][0][message[2]][message[3]] != message[4]:
                            chests[(message[5], message[6])][0][message[2]][message[3]] = message[4]
                            for i in chests[(message[5], message[6])][1]:
                                sendQueue.put(((8, 'chest', chests[(message[5], message[6])][0]), i))

                    elif message[1] == 'furnace':
                        if furnaces[message[2], message[3]][0] != message[4]:
                            furnaces[message[2], message[3]][0] = message[4]
                            for i in furnaces[message[2], message[3]][1]:
                                sendQueue.put(((8, 'furnace', furnaces[message[2], message[3]][0]), i))


                elif command == 9:

                    messageQueue.put(((10, "%s has disconnected from the game"%username_dict[address]), ('127.0.0.1', 0000)))
                    #rahprint('Player %s has disconnected from the game. %s' % (username_dict[address], address))
                    playerNDisconnect.append(players[address].number)
                    PlayerData[username_dict[address]] = players[address].save()
                    offPlayer = username_dict[address]
                    username.remove(offPlayer)

                    del players[address]
                    del username_dict[address]

                    for i in players:
                        sendQueue.put(((9, offPlayer), i))

                elif command == 10:

                    send_message = ''

                    if message[1].lower()[0] == '/':
                        if (message[1].lower().split(' ')[0][1:] in op_commands and address in players and username_dict[address] in op) or message[1].lower().split(' ')[0][1:] not in op_commands or address == ('127.0.0.1', 0):

                            if message[1].lower() == "/quit":

                                for player in players:

                                    sendQueue.put(((11, '\n\n\nDisconnected\n\nServer closed'), player))
                                    send_message = 'Server closed'

                                time.sleep(5)

                                log_process.terminate()
                                receiver.terminate()
                                sender.terminate()
                                commandline.terminate()
                                heart_beat.terminate()
                                server.close()
                                world.save()
                                break

                            elif message[1].lower() == "/delworld":
                                send_message = "<Rahmish Empire> CONFIRM: DELETE WORLD? THIS CHANGE IS PERMANENT (y/n) [n]: "

                                sys.stdout.flush()
                                in_put = messageQueue.get()
                                while in_put[0][0] != 10:
                                    # rahprint(in_put)
                                    in_put = messageQueue.get()

                                if in_put[0][1] == 'y':
                                    os.remove("saves/world.pkl")
                                    send_message = "World deleted successfully\nServer will shutdown"
                                    receiver.terminate()
                                    sender.terminate()
                                    commandline.terminate()
                                    log_queue.terminate()
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

                            elif message[1].lower()[:6] == '/clear':
                                players[address].inventory =[[[randint(1, 15), randint(1, 64)] for _ in range(9)] for __ in range(3)]
                                players[address].hotbar = [[8, 64] for _ in range(9)]

                            elif message[1].lower()[:5] == '/give':

                                message_list = message[1].split(' ')

                                executor = username_dict[address]
                                command_receiver = message_list[1]
                                item, quantity = message_list[2], message_list[3]

                                for player in players:
                                    if players[player].username == command_receiver:

                                        players[player].inventory, players[player].hotbar = give_item(
                                            players[player].inventory, players[player].hotbar, int(item), int(quantity))

                                        sendQueue.put(((15, players[player].hotbar, players[player].inventory), player))

                                        #players[player].hotbar[0] = [int(item), int(quantity)]
                                        #players[player].change_inventory_all(players[player].inventory, players[player].hotbar)

                                send_message = '%s gave %s %s of %s'%(executor, command_receiver, quantity, item)

                            elif message[1].lower()[:5] == '/kick':

                                message_list = message[1].split(' ')

                                if len(message_list) > 1:

                                    kick_name = message_list[1]
                                    if len(message_list) > 2:
                                        kick_message = ' '.join(message_list[2:])
                                    else:
                                        kick_message = ''

                                    for player in players:
                                        if players[player].username == kick_name:
                                            sendQueue.put(((11, '\n\n\nDisconnected from server by %s\n\n%s'%(username_dict[address], kick_message)), player))
                                            send_message = '%s was disconnected from the server by %s'%(kick_name, username_dict[address])

                                    if not send_message:
                                        send_message = 'Player %s not found'%kick_name

                                else:
                                    send_message = 'No parameters given'

                            elif message[1].lower()[:3] == '/tp':

                                message_list = message[1].split(' ')
                                executor = username_dict[address]
                                command_receiver = message_list[1]

                                for player in players:
                                    if players[player].username == command_receiver:

                                        x, y = players[player].change_location((list(map(int, message_list[2:4]))))

                                        for i in players:
                                            sendQueue.put(((1, players[player].username, x, y, True), i))

                                send_message = '%s teleported %s to %s %s' % (executor, command_receiver, x, y)

                            elif message[1].lower()[:3] == '/op':

                                message_list = message[1].split(' ')

                                if len(message_list) == 3:

                                    executor = username_dict[address]
                                    command_receiver = message_list[2]

                                    if message_list[1] == 'add':
                                        op.append(command_receiver)
                                        send_message = '%s gave %s op'%(executor, command_receiver)

                                        with open('data/op.rah', 'w') as op_file:
                                            for user in op:
                                                op_file.write('%s\n'%user)

                                    elif message_list[1] == 'remove':
                                        if command_receiver in op:
                                            del op[op.index(command_receiver)]

                                            with open('data/op.rah', 'w') as op_file:
                                                for user in op:
                                                    op_file.write('%s\n' % user)

                                            send_message = 'User %s was removed from the op list' % command_receiver
                                        else:
                                            send_message = 'User %s was not found in the op list'%command_receiver

                                    else:
                                        send_message = 'Unknown subcommand %s'%message_list[1]

                                else:
                                    send_message = 'No parameters given'

                            elif message[1].lower()[:4] == '/ban':

                                message_list = message[1].split(' ')

                                if len(message_list) > 1:
                                    executor = username_dict[address]
                                    command_receiver = message_list[1]

                                    if len(message_list) >= 3:
                                        ban_message = ' '.join(message_list[2:])
                                    else:
                                        ban_message = 'Queen Rahma has spoken!'

                                    ban[command_receiver] = {"message":ban_message}

                                    with open('data/ban.json', 'w') as ban_data:
                                        json.dump(ban, ban_data, indent=4, sort_keys=True)

                                    send_message = "%s banned %s for %s"%(executor, command_receiver, ban_message)

                                    for player in players:
                                        if players[player].username == command_receiver:
                                            sendQueue.put(((11, '\n\n\nDisconnected from server\n\n%s'%ban_message), player))


                                else:
                                    send_message = "Invalid parameters"


                            elif message[1].lower()[:7] == '/pardon':

                                message_list = message[1].split(' ')

                                if len(message_list) == 2:
                                    executor = username_dict[address]
                                    command_receiver = message_list[1]

                                    if command_receiver in ban:

                                        del ban[command_receiver]

                                        with open('data/ban.json', 'w') as ban_data:
                                            json.dump(ban, ban_data, indent=4, sort_keys=True)

                                        send_message = "%s pardoned %s"%(executor, command_receiver)

                                    else:
                                        send_message = "%s was not found in the ban list"%(command_receiver)

                                else:
                                    send_message = "Invalid parameters"

                            elif message[1].lower()[:10] == '/whitelist':

                                message_list = message[1].split(' ')

                                if len(message_list) == 2:
                                    if message_list[1] == 'toggle':
                                        whitelist_enable = not whitelist_enable

                                        if whitelist_enable:
                                            send_message = 'Whitelist enabled by %s'%username_dict[address]
                                        else:
                                            send_message = 'Whitelist disabled by %s' % username_dict[address]

                                        with open("data/config.rah", "w") as config_file:

                                            config = config.read().strip().split("\n")
                                            config_list = [host,
                                                           port,
                                                           world_name,
                                                           slack_enable,
                                                           channel,
                                                           online,
                                                           whitelist_enable]

                                            for line in config_list:
                                                config_file.write(line + '\n')


                                elif len(message_list) == 3:

                                    executor = username_dict[address]
                                    command_receiver = message_list[2]

                                    if message_list[1] == 'add':
                                        whitelist.append(command_receiver)
                                        send_message = '%s added %s to the whitelist'%(executor, command_receiver)

                                        with open('data/whitelist.rah', 'w') as whitelist_file:
                                            for user in whitelist:
                                                whitelist_file.write('%s\n'%user)

                                    elif message_list[1] == 'remove':
                                        if command_receiver in whitelist:
                                            del whitelist[whitelist.index(command_receiver)]

                                            with open('data/whitelist.rah', 'w') as whitelist_file:
                                                for user in whitelist:
                                                    whitelist_file.write('%s\n' % user)

                                            send_message = 'User %s was removed from the whitelist' % command_receiver
                                        else:
                                            send_message = 'User %s was not found in the whitelist'%command_receiver

                                    else:
                                        send_message = 'Unknown subcommand %s'%message_list[1]

                                else:
                                    send_message = 'No parameters given'

                            elif message[1].lower()[:5] == '/exec':
                                try:
                                    exec(message[1][6:])
                                    send_message = "Command '%s' executed by %s" % (message[1][6:], username_dict[address])
                                except:
                                    send_message = "Command '%s' failed to execute: %s" % (message[1][6:], traceback.format_exc().replace('\n',''))

                            elif message[1].lower()[:5] == '/bash':

                                try:
                                    rahprint(Popen(split(message[1][6:]), stdout=PIPE))
                                    send_message = "Bash command '%s' executed by %s" % (message[1][6:], username_dict[address])
                                except:
                                    send_message = "Bash command '%s' failed to execute: %s" % (message[1][6:], traceback.format_exc().replace('\n',''))

                            elif message[1].lower()[:5] == '/sync':
                                sendQueue.put(((14, 10000, 100, players[address].cord[0], players[address].cord[1],
                                                players[address].hotbar, players[address].inventory, playerLocations,
                                                players[address].health, players[address].hunger), address))

                                messageQueue.put(((100, round(time.time(), 3), 0), ("127.0.0.1", 0000)))
                                send_message = "Server synchronized"

                            elif message[1].lower()[:5] == '/list':
                                send_message = str(players)

                            else:
                                send_message = "Command not found"

                        else:
                            send_message = "Access denied"

                    else:
                        user_sending = username_dict[address]

                        send_message = '[%s] %s' % (user_sending, message[1])

                    if send_message[0] != '[':
                        print("broken")
                        send_message = '[%s] '%username_dict[('127.0.0.1', 0)] + send_message

                    for i in players:
                        sendQueue.put(((10, send_message), i))

                    log_queue.put('[%s]'%datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +send_message)

                    if slack_enable:
                        broadcast(channel, send_message)

                elif command == 12:
                    #Health
                    # Data: [12, <cordx>, <cordy>]
                    players[address].health = message[0]

                elif command == 13:
                    #Hunger
                    # Data: [13, <cordx>, <cordy>]
                    players[address].hunger = message[0]

                elif command == 14:
                    #Complete sync
                    sendQueue.put(((14, 10000, 100, players[address].cord[0], players[address].cord[1],
                                    players[address].hotbar, players[address].inventory, playerLocations,
                                    players[address].health, players[address].hunger), address))


                elif command == 100:

                    kill_list = []

                    for p in players:
                        if p in active_players:
                            for repeat in range(5):
                                sendQueue.put((message, p))

                        else:
                            kill_list.append(p)

                    for p in kill_list:

                        send_message = '[Server] %s was disconnected for not responding' % (players[p].username)

                        for i in players:
                            sendQueue.put(((10, send_message), i))

                        if slack_enable:
                            broadcast(channel, send_message)

                        playerNDisconnect.append(players[p].number)
                        PlayerData[players[p].username] = players[p].save()
                        offPlayer = players[p].username
                        username.remove(offPlayer)

                        del players[p]
                        del username_dict[p]

                        for i in players:
                            sendQueue.put(((9, offPlayer), i))

                    broadcast(channel, '[Tick] %s' % message[2])

                    active_players = []

                elif command == 101:
                    if address not in active_players:
                        active_players.append(address)
                    rahprint('[Server] %s has responded to heartbeat' % message[1])

            else:
                sendQueue.put(((11, '\n\n\nDisconnected from server\n\nAccess denied'), address))


        except:
            sendQueue.put(((11, '\n\n\nDisconnected from server'), address))

            print(traceback.format_exc())