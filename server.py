import socket
import pyaudio
from threading import Thread
import traceback
import json
import struct
from copy import deepcopy
import random
import threading
from tkinter import *
from GUI import Window

buf_size = 1024

class Server(Thread):

    def __init__(self, root):
        super().__init__()
        self.host = '127.0.0.1'
        self.port = random.randrange(1024, 9999)
        self.client_list = []
        self.connection_list = {}
        self.sending_receiving_list = []
        # keeps a tuple of 3 elements:
        #   1.sending client address
        #   2.receiving client address
        #   3.whether the request has been accepted or not
        ############################################
        # create a socket with ipv4 and TCP protocol
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tcp_soc.bind((self.host, self.port))
        self.udp_soc.bind((self.host, self.port))

        self.root = root
        self.tcp_soc.listen(4)

    def run(self):
        root1 = Toplevel(self.root)
        root1.wm_geometry("800x500")
        self.sender_window = Window(root1, "server")
        while True:
            temp = len(self.client_list)
            connection, client_address = self.tcp_soc.accept()
            self.client_list.append(client_address)
            self.connection_list[client_address] = [connection, self.udp_soc]
            # if temp != len(self.client_list):
            # for child in self.sender_window.winfo_children():
            #     child.destroy()
            self.sender_window.server_init_window(self.client_list)
            print("server: Connected with " + client_address[0] + ":" + str(client_address[1]))

            try:
                Thread(target=self.handle_tcp_messages, args=(connection, client_address)).start()
            except:
                self.sender_window.server_warning()
                print("TCP Thread did not start.")
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
            self.sender_window.server_messages(msg.get('request'), client_address[1])
            print('server:', str(client_address[1]), '-->', msg)

            if msg.get('request') == 'GetClintList':
                client_list_copy = deepcopy(self.client_list)
                client_list_copy.remove(client_address)
                packet = json.dumps({'ReplyClientList': client_list_copy}).encode('utf-8')
                self.sender_window.server_messages(packet, 'server')
                length = struct.pack('!I', len(packet))
                packet = length + packet
                connection.sendall(packet)

            elif msg.get('request') == 'RequestToSend':
                packet = msg
                self.sender_window.server_messages(packet, client_address[1])
                # self.gui(client_address[0] + str(client_address[1]) + ' sent' + '<RequestToSend>')
                to = packet.pop('to')
                # check the validity of the receiving client address
                if (to[0], to[1]) in self.client_list:

                    packet['from'] = client_address
                    packet = json.dumps(packet).encode('utf-8')
                    length = struct.pack('!I', len(packet))
                    packet = length + packet
                    dest = (to[0], to[1])
                    self.sender_window.server_messages(packet, 'server' , to)
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

                # check if this client is allowed to send an accept request and who is the sender
                for element in self.sending_receiving_list:
                    if element[1] == client_address:
                        if element[2] is False:
                            # allowed
                            to = element[0]
                            packet['from'] = client_address
                            packet = json.dumps(packet).encode('utf-8')
                            length = struct.pack('!I', len(packet))
                            packet = length + packet
                            i = self.sending_receiving_list.index((to, client_address, False))
                            # update the sending receiving list
                            self.sending_receiving_list[i] = (to, client_address, True)
                            self.connection_list[to][0].sendall(packet)
                            # if sample_width is not None and channels is not None and rate is not None:

                            try:
                                print('yesssssssssssss')
                                Thread(target=self.handle_udp_messages, args=(to, client_address)).start()
                            except:
                                print("UDP Thread did not start.")
                                traceback.print_exc()
                        else:
                            msg = {
                                'request': 'InvalidRequest'
                            }
                            packet = json.dumps(msg).encode('utf-8')
                            length = struct.pack('!I', len(packet))
                            packet = length + packet
                            connection.sendall(packet)
                            connection.close()
                        break
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
                    'request': 'InvalidRequest'
                }
                packet = json.dumps(msg).encode('utf-8')
                length = struct.pack('!I', len(packet))
                packet = length + packet
                connection.sendall(packet)
                connection.close()

    def handle_udp_messages(self, sending_client_address, receiving_client_address):
        # get udp messages
        # print('id:', threading.current_thread().ident)
        # x = random.randrange(0, 100)
        # file = str(x) + '.wav'
        # audio = open(file, 'wb')

        data, address = self.udp_soc.recvfrom(buf_size)
        print(address, sending_client_address, self.port, )
        try:
            while data:
                if address == sending_client_address and (sending_client_address, receiving_client_address, True) in \
                        self.sending_receiving_list:
                    # audio.write(data)
                    self.udp_soc.sendto(data, receiving_client_address)
                    self.udp_soc.settimeout(1)
                    data, address = self.udp_soc.recvfrom(buf_size)
        except socket.timeout:
            print(threading.current_thread().ident,'bye')
            # audio.close()
            self.sending_receiving_list.remove((sending_client_address, receiving_client_address, True))

