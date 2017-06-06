import pickle
import socket
import traceback
from multiprocessing import *

host = input('Host: ')
port = int(input('Port: '))


def player_sender(send_queue, server):
    print('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    print('Ready to receive command...')

    while True:
        msg = server.recvfrom(163840)
        message_queue.put(pickle.loads(msg[0]))


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVERADDRESS = (host, port)

send_queue = Queue()
message_queue = Queue()

# server.sendto(pickle.dumps([0, username, token]), SERVERADDRESS)

sender = Process(target=player_sender, args=(send_queue, server))
sender.start()

receiver = Process(target=receive_message, args=(message_queue, server))
receiver.start()

send_queue.put((pickle.dumps([0, 'henry', 'd0cf9ea0-f1b0-405b-8552-e406f2845888']), SERVERADDRESS))

while True:
    try:
        input_message = input('>>> ').split(' // ')

        print(input_message)

        server.sendto(pickle.dumps([int(input_message[0]), input_message[1]]), SERVERADDRESS)

        server_message = message_queue.get_nowait()
        print(server_message)

    except:
        print(traceback.format_exc())
