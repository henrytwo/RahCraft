import socket
from multiprocessing import *
import pickle
import time


players = {}

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

if __name__ == '__main__':
    host, port = '127.0.0.1', 1234

    auth_server = ('127.0.0.1', 1111)

    sendQueue = Queue()
    messageQueue = Queue()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Server binded to %s:%i" % (host, port))

    receiver = Process(target=receive_message, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=player_sender, args=(sendQueue, server))
    sender.start()

    while True:
        pickled_message = messageQueue.get()
        message = pickled_message[0]

        if pickled_message[1] != auth_server:
            address = pickled_message[1]

        print(pickled_message)
        command = message[0]

        if command == 2: #Login
            server.sendto(pickle.dumps([1, message[1]]), auth_server)

        elif command == 3: #Ping
            sendQueue.put(((3, str(time.time())), address))

        elif command == 10:
            sendQueue.put(((2, message[1]), address))