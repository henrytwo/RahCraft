import socket
from multiprocessing import *
import pickle

def player_sender(send_queue, server):
    print('Sender running...')

    while True:
        tobesent = send_queue.get()
        server.sendto(pickle.dumps(tobesent[0], protocol=4), tobesent[1])


def receive_message(message_queue, server):
    print('Ready to receive command...')

    while True:
        msg = server.recvfrom(16384)
        message_queue.put(pickle.loads(msg[0]))

if __name__ == '__main__':
    host, port = '127.0.0.1', 1111

    sendQueue = Queue()
    messageQueue = Queue()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _server = (host, port)

    send_queue = Queue()
    message_queue = Queue()

    sender = Process(target=player_sender, args=(send_queue, server))
    receiver = Process(target=receive_message, args=(message_queue, server))

    credentials = [input("Username: "),input("Password: ")]

    server.sendto(pickle.dumps([0, credentials]), _server)

    sender.start()
    receiver.start()

    while True:
        first_message = message_queue.get()

        if first_message == (400,):

            print("Invalid credentials")

            credentials = [input("Username: "),input("Password: ")]
            server.sendto(pickle.dumps([0, credentials]), _server)


        elif first_message[0] == 1:
            token = str(first_message[1])

            print("Login successful " + token)

            server.sendto(pickle.dumps([2, [credentials[0],token]]), ('127.0.0.1', 1234))

        elif first_message[0] == 2:
            if first_message[1] == 1:
                print("Connected to server")

            else:
                print("Disconnected. Invalid token!")
                sender.terminate()
                receiver.terminate()
                exit()

        elif first_message[0] == 3:
            print("[Server]", first_message[1])


