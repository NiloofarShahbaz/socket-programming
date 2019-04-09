import socket
import pyaudio
from threading import Thread
import traceback
import json
import struct
from copy import deepcopy


class Server(Thread):

    def __init__(self):
        super().__init__()
        self.host = '127.0.0.1'
        self.port = 1041
        self.client_list = []
        # create a socket with ipv4 and TCP protocol
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tcp_soc.bind((self.host, self.port))
        self.udp_soc.bind((self.host, self.port))

        self.tcp_soc.listen(4)
        print("TCP Socket now listening")

    def run(self):
        while True:
            connection, client_address = self.tcp_soc.accept()
            self.client_list.append(client_address)
            print("Connected with " + client_address[0] + ":" + str(client_address[1]))

            try:
                Thread(target=self.run_thread, args=(connection, client_address)).start()
            except:
                print("Thread did not start.")
                traceback.print_exc()

    def run_thread(self, connection, client_address):
        is_active = True

        while is_active:
            msg = connection.recv(1024)
            if msg == b'GetClintList':
                print(client_address[0], str(client_address[1]), ' : <GetClintList>')
                client_list_copy = deepcopy(self.client_list)
                client_list_copy.remove(client_address)
                packet = json.dumps({'ReplyClientList': client_list_copy}).encode('utf-8')
                length = struct.pack('!I', len(packet))
                packet = length + packet
                connection.sendall(packet)









# data, udp_addr = self.udp_soc.recvfrom(1024)

#
#
# f = open(data.strip(), 'wb')
#
# try:
#     while (data):
#         f.write(data)
#         udp_soc.settimeout(2)
#         data, addr = udp_soc.recvfrom(1024)
# except socket.timeout:
#     f.close()
#     udp_soc.close()
#     print("File Downloaded")
#
