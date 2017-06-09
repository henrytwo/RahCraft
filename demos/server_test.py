from socket import *
from select import select


def read_tcp(s):
    client, addr = s.accept()
    data = client.recv(8000)
    client.send('ping'.encode('UTF-8'))
    client.close()
    print('TCP: %s' % data)


def read_udp(s):
    data, addr = s.recvfrom(8000)
    print('UDP: %s' % data)


def server():
    host = ''
    port = 8888
    size = 8000
    backlog = 5

    tcp = socket(AF_INET, SOCK_STREAM)
    tcp.bind(('', port))
    tcp.listen(backlog)

    udp = socket(AF_INET, SOCK_DGRAM)
    udp.bind(('', port))

    input = [tcp, udp]

    while True:
        inputready, outputready, exceptready = select(input, [], [])

        for s in inputready:
            if s == tcp:
                read_tcp(s)
            elif s == udp:
                read_udp(s)
            else:
                print('Unknown socket:', s)


if __name__ == '__main__':
    server()
