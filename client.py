import socket
import json
import struct
import random
from os import path
from threading import Thread
import mutagen


class Client(Thread):
    def __init__(self, host, port, sendFlag=True):
        super().__init__()
        self.sendFlag = sendFlag
        self.server_host = host
        self.server_port = port
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False

    def send(self):
        client_list = self.get_client_list()
        while not len(client_list):
            # repeat until there's a client
            client_list = self.get_client_list()

        receiving_client_address = random.choice(client_list)
        client_answer, audio_size = self.request_to_send(receiving_client_address)
        if client_answer is None:
            return
        if client_answer == 'accept':
            self.send_audio(receiving_client_address, audio_size)

    def receive(self):
        self.get_request()

    def send_audio(self, receiving_client_address, audio_size):
        msg = {
            'request': 'SendAudio',
            'to': receiving_client_address,
            'audio_size': audio_size
        }
        packet = json.dumps(msg).encode('utf-8')
        length = struct.pack('!I', len(packet))
        packet = length + packet
        # self.udp_soc.sendto(packet, (self.server_host, self.server_port))

        audio = open('dgdg.mp3', 'rb')
        data = audio.read(1024)
        while data:
            if self.udp_soc.sendto(data, (self.server_host, self.server_port)):
                data = audio.read(1024)
        audio.close()

    def request_to_send(self, receiving_client_address):
        request = 'RequestToSend'
        audio = open('dgdg.mp3', 'rb')
        audio_name = path.basename(audio.name)
        audio_size = path.getsize(audio.name)
        audio_name, audio_format = path.splitext(audio_name)
        audio_format = audio_format[1:]
        audio.close()
        audio = mutagen.File('dgdg.mp3')
        audio_bitrate = audio.info.bitrate
        msg = {'request': request,
               'to': receiving_client_address,
               'audio_name': audio_name,
               'audio_size': audio_size,
               'audio_format': audio_format,
               'audio_bitrate': audio_bitrate}
        packet = json.dumps(msg).encode('utf-8')
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.tcp_soc.sendall(packet)

        # wait for reply
        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))

        msg = json.loads(buf.decode('utf-8'))
        print('Server -->', msg)
        if msg.get('request') == 'AcceptRequest':
            client_answer = msg.get('answer')
            return client_answer, audio_size
        else:
            self.connected = False

    def get_request(self):
        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        msg = json.loads(buf.decode('utf-8'))
        print('Server -->', msg)

        if msg.get('request') == 'RequestToSend':
            msg = {'request': 'AcceptRequest',
                   'answer': 'accept',
                   'to': msg.get('from')}
            packet = json.dumps(msg).encode('utf-8')
            length = struct.pack('!I', len(packet))
            packet = length + packet
            self.tcp_soc.sendall(packet)

        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        msg = json.loads(buf.decode('utf-8'))
        if msg:
            print('Server -->', msg)
            self.connected = False

    def get_client_list(self):
        msg = {'request': 'GetClintList'}
        packet = json.dumps(msg).encode('utf-8')
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.tcp_soc.sendall(packet)

        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        msg = json.loads(buf.decode('utf-8'))
        print('Server -->', msg)

        client_list = msg.get('ReplyClientList')

        return client_list

    def run(self):
        # while True:
            if not self.connected:
                self.tcp_soc.connect((self.server_host, self.server_port))
                self.connected = True
                print('Connected to server')

            if self.sendFlag:
                self.send()
            else:
                self.receive()



