import socket
import pickle
import struct
from threading import Thread


class Client(Thread):
    def __init__(self, host, port, sendFlag=True):
        super().__init__()
        self.sendFlag = sendFlag
        self.server_host = host
        self.server_port = port
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tcp_soc.connect((host, port))
        print('Connected to server')

    def send(self):
        client_list = self.get_client_list()

    def get_client_list(self):
        self.tcp_soc.sendall(b'CLIENT LIST')

        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        client_list = pickle.loads(buf)

        print(client_list)
        return client_list


    def run(self):
        if self.sendFlag:
            self.send()
            self.sendFlag = False

#
# soc.sendto(b'salam', (host, port))
# with open('/home/niloo/Music/dgdg.mp3', 'rb') as f:
#     data = f.read(1024)
#     while data:
#         if soc.sendto(data, (host, port)):
#             print('sending :|')
#             data = f.read(1024)
# soc.close()
# f.close()
