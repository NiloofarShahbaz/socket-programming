import socket
import pyaudio
from threading import Thread
import traceback
import json
import struct
from copy import deepcopy
import random


class Server(Thread):

    def __init__(self):
        super().__init__()
        self.host = '127.0.0.1'
        self.port = random.randrange(1024, 9999)
        self.client_list = []
        self.connection_list = {}
        self.sending_receiving_list = []  # keeps a tuple of 3 elements -->
        # 1.sending client address
        # 2.receiving client address
        # 3.whether it is accepted or not
        ############################################
        # create a socket with ipv4 and TCP protocol
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tcp_soc.bind((self.host, self.port))
        self.udp_soc.bind((self.host, self.port))

        self.tcp_soc.listen(4)

    def run(self):
        while True:
            connection, client_address = self.tcp_soc.accept()
            self.client_list.append(client_address)
            self.connection_list[client_address] = [connection, self.udp_soc]
            print("Connected with " + client_address[0] + ":" + str(client_address[1]))

            try:
                Thread(target=self.run_thread, args=(connection, client_address)).start()
            except:
                print("Thread did not start.")
                traceback.print_exc()

    def run_thread(self, connection, client_address):

        try:
            Thread(target=self.handle_tcp_messages, args=(connection, client_address)).start()
        except:
            print("TCP Thread did not start.")
            traceback.print_exc()

        try:
            Thread(target=self.handle_udp_messages).start()
        except:
            print("UDP Thread did not start.")
            traceback.print_exc()

    def handle_tcp_messages(self, connection, client_address):
        is_active = True

        # get tcp messages
        while is_active:
            buf = b''
            while len(buf) < 4:
                buf += connection.recv(4 - len(buf))
            length = struct.unpack('!I', buf)[0]

            buf = b''
            while len(buf) < length:
                buf += connection.recv(length - len(buf))
            msg = json.loads(buf.decode('utf-8'))
            print(client_address[0], ':', str(client_address[1]), '-->', msg)

            if msg.get('request') == 'GetClintList':
                client_list_copy = deepcopy(self.client_list)
                client_list_copy.remove(client_address)
                packet = json.dumps({'ReplyClientList': client_list_copy}).encode('utf-8')
                length = struct.pack('!I', len(packet))
                packet = length + packet
                connection.sendall(packet)

            elif msg.get('request') == 'RequestToSend':
                packet = msg
                to = packet.pop('to')

                # check the validity of the receiving client address
                if (to[0], to[1]) in self.client_list:

                    packet['from'] = client_address
                    packet = json.dumps(packet).encode('utf-8')
                    length = struct.pack('!I', len(packet))
                    packet = length + packet
                    dest = (to[0], to[1])
                    self.connection_list[dest][0].sendall(packet)
                    self.sending_receiving_list.append((client_address, dest, False))
                else:
                    msg = {
                        'request': 'NoSuchClient'
                    }
                    packet = json.dumps(msg).encode('utf-8')
                    length = struct.pack('!I', len(packet))
                    packet = length + packet
                    connection.sendall(packet)
                    connection.close()

            elif msg.get('request') == 'AcceptRequest':
                packet = msg
                to = packet.pop('to')

                # check the validity of the receiving client address
                if (to[0], to[1]) in self.client_list:
                    # if someone has send a RequestToSend request to this client and it is not accepted yet
                    if ((to[0], to[1]), client_address, False) in self.sending_receiving_list:
                        packet['from'] = client_address
                        packet = json.dumps(packet).encode('utf-8')
                        length = struct.pack('!I', len(packet))
                        packet = length + packet
                        dest = (to[0], to[1])
                        i = self.sending_receiving_list.index(((to[0], to[1]), client_address, False))
                        self.sending_receiving_list[i] = ((to[0], to[1]), client_address, True)
                        self.connection_list[dest][0].sendall(packet)
                    else:
                        msg = {
                            'request': 'InvalidRequest'
                        }
                        packet = json.dumps(msg).encode('utf-8')
                        length = struct.pack('!I', len(packet))
                        packet = length + packet
                        connection.sendall(packet)
                        connection.close()

                else:
                    msg = {
                        'request': 'NoSuchClient'
                    }
                    packet = json.dumps(msg).encode('utf-8')
                    length = struct.pack('!I', len(packet))
                    packet = length + packet
                    connection.sendall(packet)
                    connection.close()

    def handle_udp_messages(self):
        # get udp messages
        while True:
            buf = b''
            while len(buf) < 4:
                packet, client_address = self.udp_soc.recvfrom(4 - len(buf))
                buf += packet
            length = struct.unpack('!I', buf)[0]

            while len(buf) < length:
                packet, client_address = self.udp_soc.recvfrom(length - len(buf))
                buf += packet

            print('packet', buf)
            f = open(packet.strip(), 'wb')
            try:
                while packet:
                    f.write(packet)
                    self.udp_soc.settimeout(4)
                    data, addr = self.udp_soc.recvfrom(1024)
            except socket.timeout:
                f.close()
                self.udp_soc.close()
                print("File Downloaded")