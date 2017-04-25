import pickle
import socket
from multiprocessing import *
import sys
import numpy as np

sendQueue = Queue()

def playerSender(sendQueue, server):
    print('Client running...')

    while True:
        tobesent = sendQueue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def recieveMessage(server):
    print('Client is ready for connection!')

    while True:
        msg = server.recvfrom(4096)
        print('Recieved data:')
        print(pickle.loads(msg[0]), msg[1])


if __name__ == '__main__':
    with open("config", "r") as config:
        config = config.read().split("\n")
        host = config[0]
        port = int(config[1])
        worldname = config[2]

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Server binded to %s:%i" % (host, port))
    
    server.sendto(pickle.dumps([0, 'Henry']), (host, port))

    reciever = Process(target=recieveMessage, args=(server,))
    reciever.start()

    sender = Process(target=playerSender, args=(sendQueue, server))
    sender.start()

    while True:
        msg = input()
        sendQueue.put((msg.split(), (host, port)))
