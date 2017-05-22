import socket
from multiprocessing import *
import pickle
import uuid
import MySQLdb
import time


def import_users(que, thing):

	while True:
		user = {}

		db = MySQLdb.connect(host = 'localhost',
		     user = 'root',
		     passwd = '',
	             db = 'Rahmish')

		cur = db.cursor()

		cur.execute("SELECT * FROM data")

		for group in cur.fetchall():
			user[group[1]] = group[2]

		db.close()

		print("[Update]",user)

		que.put(user)

		time.sleep(10)


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


def login(credentials, user):

    print("[Login]", user, credentials)

    if credentials[0] in user and user[credentials[0]] == credentials[1]:
            sendQueue.put(((1, token(credentials)), address))

    else:
        sendQueue.put(((400,), address))

    print("[Tokens]",tokens)

def auth(credentials):

    if credentials[0] in tokens and tokens[credentials[0]] == credentials[1]:
        sendQueue.put(((10, 1), address))

    else:
        sendQueue.put(((10, 0), address))

if __name__ == '__main__':
    host, port = 'rahmish.com', 1111

    user = {}

    sendQueue = Queue()
    messageQueue = Queue()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print("Auth Server binded to %s:%i" % (host, port))

    thing = None

    user_queue = Queue()

    receiver = Process(target=receive_message, args=(messageQueue, server))
    receiver.start()

    sender = Process(target=player_sender, args=(sendQueue, server))
    sender.start()

    user_update = Process(target=import_users, args=(user_queue, thing))
    user_update.start()

    while True:

        user = user_queue.get()
            
        pickled_message = messageQueue.get()
        message, address = pickled_message

        print("[address]",message)
        command = message[0]
        
        if command == 0:
            #Login
            login(message[1], user)

        elif command == 1:
            #Auth request
            auth(message[1])
