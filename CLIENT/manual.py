from multiprocessing import *

import socket
import pickle
import components.rahma as rah

def player_sender(send_queue, server):
    rah.rahprint('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    rah.rahprint('Ready to receive command...')

    while True:
        msg = server.recvfrom(163840)
        message_queue.put(pickle.loads(msg[0]))

host = input('Host:')
port = int(input('Port: '))

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVERADDRESS = (host, port)

send_queue = Queue()
message_queue = Queue()

sender = Process(target=player_sender, args=(send_queue, server))
sender.start()

receiver = Process(target=receive_message, args=(message_queue, server))
receiver.start()

while True:
    code = int(input('Code: '))
    message = input('Message: ')
    server.sendto(pickle.dumps([code, message]), SERVERADDRESS)
    first_message = message_queue.get()
    print(first_message)