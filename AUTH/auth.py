import socket
from multiprocessing import *
from threading import *
import pickle
import uuid
import MySQLdb
import time

with open("data/config.rah", "r") as config_file:
    config = config_file.read().strip().split('\n')
    
    channel = config[0]
    slack_enable = config[1]

with open("data/mysql.rah") as sql:
    passwd = sql.read().strip()


def import_users(que):
    global passwd
    
    while True:
        user = {}

        db = MySQLdb.connect(host='localhost', user='root', passwd, db='Rahmish')

        cur = db.cursor()

        cur.execute("SELECT * FROM data")

        for group in cur.fetchall():
            user[group[1]] = group[2]

        db.close()

        print("[Update]", user)

        que.put(user)

        time.sleep(10)


tokens = {}


def gen_token(credentials):

    global tokens

    username = credentials[0]
    tokens[username] = str(uuid.uuid4())

    return tokens[username]


def credential_login(credentials, user):
    print("[Login]", user, credentials)

    if credentials[0] in user and user[credentials[0]] == credentials[1]:
        return 1, gen_token(credentials)
    else:
        return 400,

def token_login(token, user, tokens):
    print("[Login]", token)

    if token[0] in user and token[0] in tokens and tokens[token[0]] == token[1]:
        return 1, token
    else:
        return 400,

def auth(token, user, tokens):

    if token[0] in user and token[0] in tokens and tokens[token[0]] == token[1]:
        return 1,
    else:
        return 400,

def receive_info(conn, addr):
    global active_user

    message = pickle.loads(conn.recv(4096))

    command = message[0]
    if command == 0:
        # Login
        reply = credential_login(message[1], user)
        conn.send(pickle.dumps(reply))

    elif command == 1:
        # Login
        reply = token_login(message[1], user, tokens)
        conn.send(pickle.dumps(reply))

    elif command == 2:
        # Auth request
        reply = auth(message[1], user, tokens)
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

    if slack_enable:
        from components.slack import *

    thing = None

    user_queue = Queue()

    user_update = Process(target=import_users, args=(user_queue,))
    user_update.start()

    local_update = Thread(target=local_user_update)
    local_update.start()

    while True:
        conn, addr = server.accept()

        active_user[addr] = Thread(target=receive_info, args=(conn, addr))
        active_user[addr].run()
