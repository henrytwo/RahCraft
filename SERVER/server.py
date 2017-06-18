#RAHCRAFT
#COPYRIGHT 2017 (C) RAHMISH EMPIRE, MINISTRY OF RAHCRAFT DEVELOPMENT
#DEVELOPED BY RYAN ZHANG, HENRY TU, SYED SAFWAAN

#server.py

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

with open("data/config.rah", "r") as config:  # Reading server settings from a file so that the settings can be easily modifiable and is saved
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

    # Returns player data for saving
    def save(self):
        return [(self.cord[0], self.cord[1]), self.spawnCord, self.inventory, self.hotbar,
                self.health, self.hunger]


# The world class contains the numpy array of the world and several useful function for easier modification of the world
class World:
    def __init__(self, world_name):  # Uses the world name to load the world from the saves
        self.overworld = pkl.load(open("saves/" + world_name + ".pkl", "rb"))
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
        tobesent = send_queue.get()  # This gets the message needed to be sent from a queue
        try:  # A try except is used here because socket will return an error if the destination address is not valid
            server.sendto(pkl.dumps(tobesent[0], protocol=4), tobesent[1])  # Pickles the message to bytes and sends to the address
        except:
            print(tobesent[0])


# A message receiver is used to prevent loss of messages due to socket overload/socket buffer is full
def receive_message(message_queue, server):
    rahprint('Server is ready for connection!')
    while True:
        try:  # A try except is needed here because the server can sometimes receive partial packet due to client crash or internet error
            message = server.recvfrom(1024)  # Receiving messages with a buffer of 1024 bits
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


# Allows command line input from server console without stopping the server
def commandline_in(commandline_queue, fn):
    rahprint('Ready for input.')
    sys.stdin = os.fdopen(fn)  # Opens and links this function/process to the main process's input stream because multiprocessing closes the input stream

    while True:
        command = input('> ')  # Getting input
        commandline_queue.put(((10, command), ('127.0.0.1', 0000)))  # Putting command into message queue for processing


# A heartbeat function to keep track of the ticks for day night cycle and to check if the player is active
def heart_beats(message_queue, global_tick, tick):
    while True:
        time.sleep(.06)  # sleeps for a little more than 0.05 seconds for because each tick is 50ms and the time is usually 10ms early
        tick += 1  # Adding one to the ticks
        global_tick.value += 1
        if tick % 100 == 0:  # Every 100 ticks have server send the time
            message_queue.put(((100, round(time.time(), 3), tick), ("127.0.0.1", 0000)))  # Add current time and the tick to help the client to predict the correct tick
            if tick >= 24000:  # Resent ticks to starting state because each day cycle is 24000 ticks
                tick = 1


# Collecting some system information just for analysis
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


# Sending messages to the authentication server ver account verification
def authenticate(message):
    global online  # Global is used here to retreve settings

    if not online:
        return True  # The game doesn't need authentication

    user, token = message

    host, port = 'rahmish.com', 1111

    socket.setdefaulttimeout(10)  # Setting a timeout to detect if the auth server is offline or not
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a TCP socket for connection to the auth server
    SERVERADDRESS = (host, port)  # Setting the server address of the auth server
    socket.setdefaulttimeout(None)  # Reseting the timeout so that other sockets wont be affected

    try:  # Try except is needed because there is no way to tell if the auth server is online or not
        server.connect(SERVERADDRESS)  # Connecting to the auth server
        server.send(pkl.dumps([2, [user, token, collect_system_info()]]))

        while True:

            first_message = pkl.loads(server.recv(10096))  # Recieving the message

            if first_message[0] == 1:  # Authentication successful
                server.close()  # Closing socket stream
                return True

            else:
                server.close()
                return False
    except:
        server.close()  # Error occured
        print(traceback.format_exc())
        return False


if __name__ == '__main__':  # Used to make sure multiprocessing does not run this part of the code
    players = {}  # Player dictionary of the current active players
    username_dict = {('127.0.0.1', 0): 'Rahbot'}  # Username dictionary translating from ip to username
    player_number = 1  # The current player number

    active_players = []  # A list of active players for heartbeat/disconnect

    playerNDisconnect = deque([])  # A double ended queue to store the player numbers that are used but the player disconnected
    move = ''

    PlayerData = {}  # Player data library of all the saved players

    sendQueue = Queue()  # Multiprocessing queue as a buffer and a way to communicate between processes
    messageQueue = Queue()
    commandlineQueue = Queue()
    log_queue = Queue()

    global_tick = Value('l', 0)  # A multiprocessing shared value to keep track of how many ticks has elapsed
    username = set()

    if slack_enable:
        config_slack()

    world = World(world_name)  # Creating a new world object to load the world

    chests = {}  # Extra world/block inventories are stored in a dictionary
    furnaces = {}
    entities = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Start a UDP socket for game server
    server.bind((host, port))  # Binding server to port and server address to listen for messages

    rahprint("Server binded to %s:%i" % (host, port))  # Debug print

    log_process = Process(target=logger, args=(log_queue,))  # Creating multiprocessing processes with queues as args for cross process communication
    log_process.start()  # Starting mltiprocessing processes

    heart_beat = Process(target=heart_beats, args=(messageQueue, global_tick, 0))
    heart_beat.start()

    receiver = Process(target=receive_message, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=player_sender, args=(sendQueue, server))
    sender.start()

    fn = sys.stdin.fileno()  # Getting the input stream of the main process
    commandline = Process(target=commandline_in, args=(messageQueue, fn))
    commandline.start()

    # Loading data files for normal server operation
    # ==============================================
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

        kill_list = [] #List of users to be kicked for death

        for player in players: #Iterates through all users
            if players[player].health <= 0: #Checks health and kicks user if health <= 0
                kick_message = "RAHDEATH:GG, You died!"

                kill_list.append(player)

                send_message = "%s died" % players[player].username

                sendQueue.put(((11, '%s' % kick_message), player))

                if send_message[0] != '[':
                        send_message = '[%s] '%username_dict[('127.0.0.1', 0)] + send_message

                for i in players:  # Broadcast message to all players for player disconnect
                    sendQueue.put(((10, send_message), i))

        for kill_player in kill_list: #Removes the players in another function so that list index does not mess up
            playerNDisconnect.append(players[kill_player].number)
            username.remove(players[kill_player].username)

            del PlayerData[players[kill_player].username]
            del players[kill_player]

        pickled_message = messageQueue.get()
        message, address = pickled_message
        command = message[0]

        try:  # A try except is used here because the messages can have some lost data causing it to not match the command requirement

            # External commands
            if command == 0:  # Commands dictates the type of data, integers are used here to transfer less data speeding up problems due to internet
                # Player login and authentication
                # Data: [0,<username>, <token>]

                if message[1] not in ban:  # Check if the player is banned or not

                    if whitelist_enable and message[1] in whitelist or not whitelist_enable:  # Check if the whitelist is enabled or not and if it is, check if the player whitelisted

                        if message[1] not in username:  # Check if there is already a player with the same username

                            if authenticate(message[1:3]):  # Authenticating the player using the function

                                if not playerNDisconnect:  # giving the player a number
                                    PN = player_number
                                    player_number += 1
                                else:
                                    PN = playerNDisconnect.popleft()

                                playerLocations = {players[x].username: players[x].cord for x in players}  # Getting the players that are online and have a x/y

                                players[address] = Player(PN, message[1])  # Creating an object on the server to store data for the player
                                username_dict[address] = message[1]

                                sendQueue.put(((0, 10000, 100, players[address].cord[0], players[address].cord[1], players[address].hotbar, players[address].inventory, playerLocations, players[address].health, players[address].hunger), address))
                                # Sending the required information to the player for the game to start
                                active_players.append(address)  # Add to activate player

                                messageQueue.put(((10, "%s has connected to the game" % message[1]), ('127.0.0.1', 0000)))  # P ut a message back into the system for broadcasting
                                username.add(message[1])  # Adding the name to a set. A set is used here because the in command can perform in O(1) time in sets

                                for i in players:  # Tells the clients to make a new remote player object for the new player
                                    if players[i].username != username_dict[address]:
                                        sendQueue.put(((1, username_dict[address], players[address].cord[0], players[address].cord[1], False), i))

                            else:
                                sendQueue.put(((400, (
                                    "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\nCredentials were rejected by\nRahCraft Authentication Service\n(Try logging in again)\n\n")),
                                               address))
                                # Auth error
                        else:
                            sendQueue.put(((400, (
                                "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\nUsername currently in use\nIf you recently disconnected,\ntry to login again")),
                                           address))
                            # Same username in use
                    else:
                        sendQueue.put(((400, (
                            "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\nThis server is white listed\nIf you believe this is an error,\nContact the administrator for assistance")),
                                       address))
                        # Reject due to whitelist
                else:
                    sendQueue.put(((400, (
                        "\n\n\n\n\n\n\n\n\nConnection closed by remote host\n\n%s" % ban[message[1]]['message'])),
                                   address))
                    # Server error

            # External heartbeat
            elif command == 102:
                sendQueue.put(((102, motd, host, port), address))  # Sends client the server's motd

            elif address in players or address == ('127.0.0.1', 0000):  # Check if player exists or is system before excuting command to pervent errors
                if command == 1:
                    # Player movement
                    # Data: [1, <cordx>, <cordy>]
                    x, y = players[address].change_location((message[1], message[2]))

                    for i in players:
                        sendQueue.put(((1, username_dict[address], x, y, False), i))  # Broadcast movement

                elif command == 2:
                    # Render world
                    # Data: [2, <cordx>, <cordy>, <size>, <blocksize>]
                    sendQueue.put(((2, message[1], message[2], world.get_world(message[1], message[2], message[3], message[4])), address))  # Gets the section of the world needed by the client and sends to the client

                elif command == 3:
                    # Break block
                    # Data: [3, <cordx>, <cordy>]
                    if hypot(world.spawnpoint[0] - message[1], world.spawnpoint[1] - message[2]) < 2:  # Check for distance to spawn to prevent griefing
                        spawnpoint_check = world.get_spawnpoint()  # Request new spawnpoint

                        if spawnpoint_check != world.spawnpoint:  # Spawnpoint changed
                            world.spawnpoint = spawnpoint_check[:]  # Set world spawnpoint

                            for i in players:
                                players[i].change_spawn(world.spawnpoint)  # Change spawn for all players

                    world.break_block(message[1], message[2])  # Break the block

                    for i in players:  # Broadcast message that a block has been broken
                        sendQueue.put(((3, message[1], message[2]), i))

                elif command == 4:
                    # Place block
                    # Data: [4, <cordx>, <cordy>, <block type>, <item slot>]
                    if hypot(world.spawnpoint[0] - message[1], world.spawnpoint[1] - message[2]) < 2:  # Check for distance to spawn to prevent griefing
                        spawnpoint_check = world.get_spawnpoint()

                        if spawnpoint_check != world.spawnpoint:
                            world.spawnpoint = spawnpoint_check[:]

                            for i in players:
                                players[i].change_spawn(world.spawnpoint)

                    world.place_block(message[1], message[2], message[3])  # Place the block
                    players[address].hotbar[message[4]][1] -= 1  # Subtract one item from the current slot

                    if players[address].hotbar[message[4]][1] <= 0 or players[address].hotbar[message[4]][0] == 0:
                        players[address].hotbar[message[4]] = [0, 0]  # Rest to 0,0 if no block is left in that slot

                    sendQueue.put(((6, message[4], players[address].hotbar[message[4]]), address))  # updates the player inventory
                    if message[3] == 17:  # If the block placed is a chest, the start add a blank chest to the chests library
                        chests[(message[1], message[2])] = [[[[0, 0] for _ in range(9)] for __ in range(3)], [address[:]]]  # adding blank chest and who is currently using the chest
                    elif message[3] == 18:  # Adding furnace
                        furnaces[(message[1], message[2])] = [[[0, 0], [0, 0], [0, 0]], [address[:]]]

                    for i in players:  # Broadcast that an Item has been placed so that the client's world updates
                        sendQueue.put(((4, message[1], message[2], message[3]), i))

                elif command == 5:  # Update the player's inventory on the server side, usually after crafting, using a chest, or furnace
                    players[address].change_inventory_all(message[1], message[2])

                elif command == 7:  # Command to request for the <storage block>'s inventory
                    if message[1] == 'chest':  # If the block pointing at is a chest
                        if message[-1] == 1:  # is opening the chest
                            if (message[2], message[3]) in chests:  # If chest exists
                                chests[(message[2], message[3])][1].append(address)  # Add player to the players who are using this chest
                                sendQueue.put(([8, 'chest', chests[message[2], message[3]][0]], address))  # Send player the storage
                            else:
                                sendQueue.put(([8, "err"], address))  # Error has occured
                        else:
                            if(message[2], message[3]) in chests:  # Closing chest
                                chests[(message[2], message[3])][1].remove(address)  # Remove player from players who are usig this chest to stop updating the player on the chests's inventory
                            else:
                                sendQueue.put(([8, "err"], address))

                    elif message[1] == 'furnace':  # Same as chests but with furnaces
                        if message[-1] == 1:
                            if (message[2], message[3]) in furnaces:
                                furnaces[(message[2], message[3])][1].append(address)
                                sendQueue.put(([8, 'furnace', furnaces[message[2], message[3]][0]], address))
                            else:
                                print(traceback.format_exc())
                                sendQueue.put(([8, "err"], address))
                        else:
                            if (message[2], message[3]) in furnaces:
                                furnaces[(message[2], message[3])][1].remove(address)
                            else:
                                print(traceback.format_exc())
                                sendQueue.put(([8, "err"], address))

                elif command == 8:  # Update the storage of the storage block
                    if message[1] == 'chest':  # If the block is a chest
                        if chests[(message[5], message[6])][0][message[2]][message[3]] != message[4]: # If the inventory provided is not equal to the one in library, update the storage
                            chests[(message[5], message[6])][0][message[2]][message[3]] = message[4]
                            for i in chests[(message[5], message[6])][1]:
                                sendQueue.put(((8, 'chest', chests[(message[5], message[6])][0]), i))  # Transmit the storage to anyone who is currently using the chest

                    elif message[1] == 'furnace':  # Same with Chests but with furnaces
                        if furnaces[message[2], message[3]][0] != message[4]:
                            furnaces[message[2], message[3]][0] = message[4]
                            for i in furnaces[message[2], message[3]][1]:
                                sendQueue.put(((8, 'furnace', furnaces[message[2], message[3]][0]), i))


                elif command == 9:  # Player is disconnecting from the server

                    messageQueue.put(((10, "%s has disconnected from the game" % username_dict[address]), ('127.0.0.1', 0000)))  # broadcast chat message
                    playerNDisconnect.append(players[address].number)  # Removing the player's playernumber to be used by another new player
                    PlayerData[username_dict[address]] = players[address].save()  # Saving the player's conditions to the library
                    offPlayer = username_dict[address]  # Temp storage of the player's username for farther use
                    username.remove(offPlayer)  # Removing player from the username set to allow this username to be used again

                    del players[address]  # Delete the player from the active players list
                    del username_dict[address]

                    for i in players:  # Broadcast message to client to remove remote player objects for this player
                        sendQueue.put(((9, offPlayer), i))

                elif command == 10:  # Server console commands and chat messages

                    send_message = ''  # Message to be sent to console and etc

                    if message[1].lower()[0] == '/':  # Check if the chat message is a command
                        if (message[1].lower().split(' ')[0][1:] in op_commands and address in players and username_dict[address] in op) or message[1].lower().split(' ')[0][1:] not in op_commands or address == ('127.0.0.1', 0):  # Check if the user has enough permissions to activate this command

                            if message[1].lower() == "/quit":  # If the command is quit

                                for player in players:  # Kick all players
                                    sendQueue.put(((11, '\n\n\nDisconnected\n\nServer closed'), player))
                                    send_message = 'Server closed'

                                time.sleep(5)  # Wait for player's to disconnect

                                log_process.terminate()  # Terminate all processes
                                receiver.terminate()
                                sender.terminate()
                                commandline.terminate()
                                heart_beat.terminate()
                                server.close()  # Close socket
                                world.save()  # Save the world
                                break # Stop the while loop

                            elif message[1].lower() == "/delworld":  # Delete the world
                                send_message = "<Rahmish Empire> CONFIRM: DELETE WORLD? THIS CHANGE IS PERMANENT (y/n) [n]: "

                                sys.stdout.flush()  # Flushing the output stream so the message can be printed on to the screen
                                in_put = messageQueue.get()  # Get whether the confirmation
                                while in_put[0][0] != 10:  # Ignore all client commands while waiting
                                    in_put = messageQueue.get()

                                if in_put[0][1] == 'y':  # If the user confirms deletion, Shutdown server, remote world, close socket, terminate all processes
                                    os.remove("saves/world.pkl")
                                    send_message = "World deleted successfully\nServer will shutdown"
                                    receiver.terminate()
                                    sender.terminate()
                                    commandline.terminate()
                                    log_queue.terminate()
                                    server.close()

                                    exit()

                                    break

                                else:  # if confirmation faliure
                                    send_message = "Command aborted"

                            elif message[1].lower() == '/ping':  # Ping command, added to match minecraft server
                                send_message = 'pong!'

                            elif message[1].lower() == '/lenin':  # Command test and network stress testing
                                with open('data/communist.rah') as communist:  # Reads a text file out to the clients
                                    for line in communist.read().split('\n'):
                                        send_message = '[Comrade Lenin] ' + line

                                        for i in players:
                                            sendQueue.put(((10, send_message), i))

                            elif message[1].lower()[:4] == '/say':  # Put something in chat as the server
                                send_message = message[1][4:]

                            elif message[1].lower()[:6] == '/clear':  # Delete the player's inventory
                                players[address].inventory = [[[randint(1, 15), randint(1, 64)] for _ in range(9)] for __ in range(3)]
                                players[address].hotbar = [[8, 64] for _ in range(9)]

                            elif message[1].lower()[:5] == '/give':  # Give the player items

                                message_list = message[1].split(' ')  # Split the message to minipulate the args

                                executor = username_dict[address]  # Who ran this command
                                command_receiver = message_list[1]  # Who is getting the items
                                item, quantity = message_list[2], message_list[3]  # What the item id is and how much of that item

                                for player in players: # Search for the player and give the person the items
                                    if players[player].username == command_receiver:
                                        players[player].inventory, players[player].hotbar = give_item(players[player].inventory, players[player].hotbar, int(item), int(quantity))  # Change the player's inventoy

                                        sendQueue.put(((15, players[player].hotbar, players[player].inventory), player))  # Update client with new item

                                send_message = '%s gave %s %s of %s' % (executor, command_receiver, quantity, item)  # Chat message

                            elif message[1].lower()[:5] == '/kick':  # Booting someone off of the server

                                message_list = message[1].split(' ')

                                if len(message_list) > 1:  # If a parameter is given

                                    kick_name = message_list[1]  # Who is kicked
                                    if len(message_list) > 2:  # kick with custom messages
                                        kick_message = ' '.join(message_list[2:])
                                    else:
                                        kick_message = ''  # no message/ default message

                                    for player in players:  # Search for the player
                                        if players[player].username == kick_name:

                                            sendQueue.put(((11, '\n\n\nDisconnected from server by %s\n\n%s' % (
                                            username_dict[address], kick_message)), player))
                                            send_message = '%s was disconnected from the server by %s' % (
                                            kick_name, username_dict[address])

                                            playerNDisconnect.append(players[player].number)
                                            PlayerData[players[player].username] = players[player].save()
                                            offPlayer = players[player].username
                                            username.remove(offPlayer)

                                            del players[player]
                                            del username_dict[player]


                                            break

                                    if not send_message:
                                        send_message = 'Player %s not found'%kick_name

                                else:  # No parameter
                                    send_message = 'No parameters given'

                            elif message[1].lower()[:3] == '/tp':  # Move a player to a location or another player

                                message_list = message[1].split(' ')
                                executor = username_dict[address]
                                command_receiver = message_list[1]

                                for player in players:  # Search for the player
                                    if players[player].username == command_receiver:

                                        x, y = players[player].change_location((list(map(int, message_list[2:4]))))  # Change the location of the player

                                        for i in players:
                                            sendQueue.put(((1, players[player].username, x, y, True), i))  # Broadcast the player's new location so clients can update the remote players

                                send_message = '%s teleported %s to %s %s' % (executor, command_receiver, x, y)  # Chat message

                            elif message[1].lower()[:4] == '/msg':

                                message_list = message[1].split(' ')
                                executor = username_dict[address]
                                command_receiver = message_list[1]

                                private_send_message = [''.join(message_list[2:]), command_receiver]


                            elif message[1].lower()[:3] == '/op':

                                message_list = message[1].split(' ')

                                if len(message_list) == 3:  # Check for the number of parameters

                                    executor = username_dict[address]
                                    command_receiver = message_list[2]

                                    if message_list[1] == 'add':  # Add admin
                                        op.append(command_receiver)  # Add to admin list
                                        send_message = '%s gave %s op' % (executor, command_receiver)

                                        with open('data/op.rah', 'w') as op_file:  # Write message to file for permanent storage
                                            for user in op:
                                                op_file.write('%s\n' % user)

                                    elif message_list[1] == 'remove':  # Same as add admin but remove
                                        if command_receiver in op:  # If the person is a admin, then remove
                                            del op[op.index(command_receiver)]

                                            with open('data/op.rah', 'w') as op_file:
                                                for user in op:
                                                    op_file.write('%s\n' % user)

                                            send_message = 'User %s was removed from the op list' % command_receiver
                                        else:
                                            send_message = 'User %s was not found in the op list' % command_receiver

                                    else:
                                        send_message = 'Unknown subcommand %s' % message_list[1]  # Something other than add or remove is given

                                else:
                                    send_message = 'No parameters given'

                            elif message[1].lower()[:4] == '/ban':  # Ban players from joining the server

                                message_list = message[1].split(' ')

                                if len(message_list) > 1:  # If there are parameters
                                    executor = username_dict[address]
                                    command_receiver = message_list[1]

                                    if len(message_list) >= 3:  # If there is a custom ban message, use that
                                        ban_message = ' '.join(message_list[2:])
                                    else:
                                        ban_message = 'Queen Rahma has spoken!'  # If not, use default

                                    ban[command_receiver] = {"message": ban_message}

                                    with open('data/ban.json', 'w') as ban_data:  # Write ban data to file
                                        json.dump(ban, ban_data, indent=4, sort_keys=True)

                                    send_message = "%s banned %s for %s" % (executor, command_receiver, ban_message)

                                    for player in players:  # Find person that is banned and remove them
                                        if players[player].username == command_receiver:
                                            sendQueue.put(
                                                ((11, '\n\n\nDisconnected from server\n\n%s' % ban_message), player))

                                    playerNDisconnect.append(players[player].number)
                                    PlayerData[players[player].username] = players[player].save()
                                    offPlayer = players[player].username
                                    username.remove(offPlayer)

                                    del players[player]
                                    del username_dict[player]

                                else:
                                    send_message = "Invalid parameters"


                            elif message[1].lower()[:7] == '/pardon':  # Unban a player Same as banning a player but doing the oppsite

                                message_list = message[1].split(' ')

                                if len(message_list) == 2:
                                    executor = username_dict[address]
                                    command_receiver = message_list[1]

                                    if command_receiver in ban:

                                        del ban[command_receiver]

                                        with open('data/ban.json', 'w') as ban_data:
                                            json.dump(ban, ban_data, indent=4, sort_keys=True)

                                        send_message = "%s pardoned %s" % (executor, command_receiver)

                                    else:
                                        send_message = "%s was not found in the ban list" % (command_receiver)

                                else:
                                    send_message = "Invalid parameters"

                            elif message[1].lower()[:10] == '/whitelist':  # allow a person to join the server

                                message_list = message[1].split(' ')

                                if len(message_list) == 2:  # if a subcommand is given
                                    if message_list[1] == 'toggle':
                                        whitelist_enable = not whitelist_enable

                                        if whitelist_enable:  # Send confirmation about whether the whitelist is disabled or enabled
                                            send_message = 'Whitelist enabled by %s' % username_dict[address]
                                        else:
                                            send_message = 'Whitelist disabled by %s' % username_dict[address]

                                        with open("data/config.rah", "w") as config_file:  # Write new config

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


                                elif len(message_list) == 3: # Something other than toggle is added

                                    executor = username_dict[address]
                                    command_receiver = message_list[2]

                                    if message_list[1] == 'add':  # Add player to whitelist
                                        whitelist.append(command_receiver)  # Add to whitelist saved in ram
                                        send_message = '%s added %s to the whitelist' % (executor, command_receiver)

                                        with open('data/whitelist.rah', 'w') as whitelist_file:  # Write to file
                                            for user in whitelist:
                                                whitelist_file.write('%s\n' % user)

                                    elif message_list[1] == 'remove':  # Sme as add to this removes player instead
                                        if command_receiver in whitelist:
                                            del whitelist[whitelist.index(command_receiver)]

                                            with open('data/whitelist.rah', 'w') as whitelist_file:
                                                for user in whitelist:
                                                    whitelist_file.write('%s\n' % user)

                                            send_message = 'User %s was removed from the whitelist' % command_receiver
                                        else:
                                            send_message = 'User %s was not found in the whitelist' % command_receiver  # Cannot find the player for removal

                                    else:
                                        send_message = 'Unknown subcommand %s' % message_list[1]  # if the subcommand not runnable by the server

                                else:
                                    send_message = 'No parameters given'  # not enough params

                            elif message[1].lower()[:5] == '/exec':  # Make the server run a python command
                                try:
                                    exec(message[1][6:])  # Run command
                                    send_message = "Command '%s' executed by %s" % (message[1][6:], username_dict[address])  # Output message is command ran with no errors
                                except:
                                    send_message = "Command '%s' failed to execute: %s" % (message[1][6:], traceback.format_exc().replace('\n', ''))  # If error, the send back the trackback

                            elif message[1].lower()[:5] == '/bash':  # Run bash commands

                                try:
                                    rahprint(Popen(split(message[1][6:]), stdout=PIPE))  # run command
                                    send_message = "Bash command '%s' executed by %s" % (message[1][6:], username_dict[address])
                                except:
                                    send_message = "Bash command '%s' failed to execute: %s" % (message[1][6:], traceback.format_exc().replace('\n', ''))

                            elif message[1].lower()[:5] == '/sync':  # Sync everything involving the player and needed for the client to function. Helps when the client looses data
                                sendQueue.put(((14, 10000, 100, players[address].cord[0], players[address].cord[1],
                                                players[address].hotbar, players[address].inventory, playerLocations,
                                                players[address].health, players[address].hunger), address))

                                messageQueue.put(((100, round(time.time(), 3), 0), ("127.0.0.1", 0000)))
                                send_message = "Server synchronized"

                            elif message[1].lower()[:5] == '/list':  # sends a list of player
                                send_message = ''.join([str([players[player].username, player]) for player in players])

                            else:
                                send_message = "Command not found"  # The command received is not found

                        else:  # Not an admin
                            send_message = "Access denied"

                    else:
                        user_sending = username_dict[address]  # normal chat, get the user sending the message

                        send_message = '[%s] %s' % (user_sending, message[1])  # Get the message eto be sent

                    if send_message[0] != '[': # If no player name is found, it must be run by the server
                        send_message = '[%s] ' % username_dict[('127.0.0.1', 0)] + send_message

                    for i in players:  # send all players the chat message
                        sendQueue.put(((10, send_message), i))

                    log_queue.put('[%s]' % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + send_message) # put something in log file

                    if slack_enable:
                        broadcast(channel, send_message)

                elif command == 12:
                    # Health
                    # Data: [12, <cordx>, <cordy>]
                    players[address].health = message[1]

                elif command == 13:
                    # Hunger
                    # Data: [13, <cordx>, <cordy>]
                    players[address].hunger = message[1]

                elif command == 14:  # Reset player's current stats to the ones saved on the sever if a problem occurs
                    # Complete sync
                    sendQueue.put(((14, 10000, 100, players[address].cord[0], players[address].cord[1],
                                    players[address].hotbar, players[address].inventory, playerLocations,
                                    players[address].health, players[address].hunger), address))


                elif command == 100:

                    kill_list = []  # Reset kill list

                    for p in players:  # Send active players a message 5 times to ensure the client recieves the message
                        if p in active_players:
                            for repeat in range(5):
                                sendQueue.put((message, p))

                        else:
                            kill_list.append(p)  # If player is not active than kill player

                    for p in kill_list:  # Loop through the player kill list and kill all players that are inactive

                        send_message = '[Server] %s was disconnected for not responding' % (players[p].username)  # chat message

                        for i in players:
                            sendQueue.put(((10, send_message), i))  # broadcast to all players that player is inactive

                        if slack_enable:  # send on slack if needed
                            broadcast(channel, send_message)

                        playerNDisconnect.append(players[p].number)  # Disconnect player
                        PlayerData[players[p].username] = players[p].save()
                        offPlayer = players[p].username
                        username.remove(offPlayer)

                        del players[p]
                        del username_dict[p]

                        for i in players:
                            sendQueue.put(((9, offPlayer), i))

                    broadcast(channel, '[Tick] %s' % message[2])  # send slack message

                    active_players = []  # Reset active player

                elif command == 101:  # Heartbeat to check if the player's client is still active
                    if address not in active_players:  # Add player replied to active player if not in already
                        active_players.append(address)
                    rahprint('[Server] %s has responded to heartbeat' % message[1])  # debugging message

            else:
                sendQueue.put(((11, '\n\n\nDisconnected from server\n\nAccess denied'), address))  # The player is not recognized and is rejected for security purposes

        except:
            sendQueue.put(((11, '\n\n\nDisconnected from server'), address))  # Disconnect if player sends faulty data

            print(traceback.format_exc())  # Crash, print crash message
