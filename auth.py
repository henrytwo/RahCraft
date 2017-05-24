import socket
from multiprocessing import *
from threading import *
import pickle
import uuid
import MySQLdb
import time


def import_users(que, thing):
    while True:
        user = {}

        db = MySQLdb.connect(host='localhost', user='root', passwd='', db='Rahmish')

        cur = db.cursor()

        cur.execute("SELECT * FROM data")

        for group in cur.fetchall():
            user[group[1]] = group[2]

        db.close()

        print("[Update]", user)

        que.put(user)

        time.sleep(10)


tokens = {}


def token(credentials):
    username = credentials[0]
    tokens[username] = str(uuid.uuid4())

    return tokens[username]


def login(credentials, user):
    print("[Login]", user, credentials)

    print("[Tokens]", tokens)

    if credentials[0] in user and user[credentials[0]] == credentials[1]:
        return 1, token(credentials)
    else:
        return (400,)


def auth(credentials):
    if credentials[0] in tokens and tokens[credentials[0]] == credentials[1]:
        return 10, 1

    else:
        return 10, 0


def recieve_info(conn, addr):
    global active_user

    message = pickle.loads(conn.recv(4096))

    command = message[0]
    if command == 0:
        # Login
        reply = login(message[1], user)
        conn.send(pickle.dumps(reply))

    elif command == 1:
        # Auth request
        reply = auth(message[1])
        conn.send(pickle.dumps(reply))

    del active_user[addr]


def local_user_update():
    global user
    while True:
        user = user_queue.get()


if __name__ == '__main__':
    host, port = 'rahmish.com', 1111

    user = {}
    active_user = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(50)

    print("Auth Server binded to %s:%i" % (host, port))

    thing = None

    user_queue = Queue()

    user_update = Process(target=import_users, args=(user_queue, thing))
    user_update.start()

    local_update = Thread(target=local_user_update)
    local_update.start()

    while True:
        conn, addr = server.accept()

        active_user[addr] = Thread(target=recieve_info, args=(conn, addr))
        active_user[addr].run()
