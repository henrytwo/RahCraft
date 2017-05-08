from pygame import *
from multiprocessing import *
import socket
import rahma
import menu
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


def game(username):
    print('Starting game')

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    send_queue = Queue()
    message_queue = Queue()





if __name__ == "__main__":
    navigation = 'login'

    size = (800, 500)
    screen = display.set_mode(size)

    rahma.rah(screen)

    init()
    font.init()

    click_cursor = ["      ..                ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX.               ",
                    "     .XX...             ",
                    "     .XX.XX...          ",
                    "     .XX.XX.XX.         ",
                    "     .XX.XX.XX...       ",
                    "     .XX.XX.XX.XX.      ",
                    "     .XX.XX.XX.XX.      ",
                    "...  .XX.XX.XX.XX.      ",
                    ".XX...XXXXXXXXXXX.      ",
                    ".XXXX.XXXXXXXXXXX.      ",
                    " .XXX.XXXXXXXXXXX.      ",
                    "  .XXXXXXXXXXXXXX.      ",
                    "  .XXXXXXXXXXXXXX.      ",
                    "   .XXXXXXXXXXXXX.      ",
                    "    .XXXXXXXXXXX.       ",
                    "    .XXXXXXXXXXX.       ",
                    "     .XXXXXXXXX.        ",
                    "     .XXXXXXXXX.        ",
                    "     ...........        "]

    click_cursor_data = ((24, 24), (7, 1), *cursors.compile(click_cursor))
    mouse.set_cursor(*cursors.tri_left)

    UI = {'login': login,
          'menu': menu,
          'about': about,
          'options': options,
          'assistance': assistance,
          'game': game,
          'server_picker': server_picker,
          'custom_server_picker': custom_server_picker,
          'local_server': local_server,
          'rahmish_server': rahmish_server}

    while navigation != 'exit':
        navigation = UI[navigation]()

    display.quit()
    raise SystemExit