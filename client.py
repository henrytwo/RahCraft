from socket import *
from multiprocessing import *
from pickle import *

server = socket(AF_INET, SOCK_DGRAM)
sendQueue = Queue()
recieveQueue = Queue()

def sender(serv, sendQueue):
    """Sender Format: [message, (ip, port)]"""
    while True:
        message = sendQueue.get()
        serv.sendto(dumps(message[0]), message[1])

def reciever(serv, recieveQueue):
    while True:
        recieveQueue.put(loads(serv.recvfrom(1024)[0]))

class Player(object):
    def __init__(self, username, ip, port):
        self.username = username
        self.cord =

    def movement(self):
        pass

    def senddata(self):
        pass

    def update(self):
        pass

