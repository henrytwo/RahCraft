from socket import *

def send_tcp(data):
        try:
                s = socket(AF_INET, SOCK_STREAM)
                s.connect(('localhost',8888))
                s.send(data.encode('UTF-8'))
                print(s.recv(8000))
                s.close()

        except:
                return True

def send_udp(data):
	s = socket(AF_INET, SOCK_DGRAM)
	s.sendto(data.encode('UTF-8'), ('localhost', 8888))
	s.close()

if __name__ == '__main__':
	while True:
		if send_tcp('heartbeat'):
			print('Connection lost')
			break
		send_udp(input('> '))
