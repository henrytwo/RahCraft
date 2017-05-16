import socket
from multiprocessing import *
import pickle
import uuid

user = {"henry":"password"}

tokens = {}

def player_sender(send_queue, server):
    print('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    print('Auth Server is ready for connection!')

    while True:
        try:
            message = server.recvfrom(1024)
        except:
            continue
        message_queue.put((pickle.loads(message[0]), message[1]))

def token(credentials):

    username = credentials[0]
    tokens[username] = str(uuid.uuid4())

    return tokens[username]


def login(credentials):
    if credentials[0] in user and user[credentials[0]] == credentials[1]:
            sendQueue.put(((1, token(credentials)), address))

    else:
        sendQueue.put(((400,), address))

    print(tokens)

def auth(credentials):

    if credentials[0] in tokens and tokens[credentials[0]] == credentials[1]:
        sendQueue.put(((10, 1), address))

    else:
        sendQueue.put(((10, 0), address))

if __name__ == '__main__':
    host, port = '127.0.0.1', 1111
    
    sendQueue = Queue()
    messageQueue = Queue()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Auth Server binded to %s:%i" % (host, port))

    receiver = Process(target=receive_message, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=player_sender, args=(sendQueue, server))
    sender.start()

    while True:
        pickled_message = messageQueue.get()
        message, address = pickled_message

        print(pickled_message)
        command = message[0]
        
        if command == 0:
            #Login
            login(message[1])

        elif command == 1:
            #Auth request
            auth(message[1])
