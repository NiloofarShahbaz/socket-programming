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

        self.tcp_soc.connect((host, port))
        print('Connected to server')

    def send(self):
        client_list = self.get_client_list()
        if len(client_list):
            receiving_client_address = random.choice(client_list)
            self.request_to_send(receiving_client_address)

    def request_to_send(self, receiving_client_address):
        request = b'RequestToSend'
        audio = open('/home/niloo/Music/dgdg.mp3', 'rb')
        audio_name = path.basename(audio.name)
        audio_size = path.getsize(audio.name)
        audio_name, audio_format = path.splitext(audio_name)
        audio_format = audio_format[1:]
        audio.close()
        audio = mutagen.File('/home/niloo/Music/dgdg.mp3')
        audio_bitrate = audio.info.bitrate
        print(audio_format, audio_name, audio_size, audio_bitrate)
        msg = {'request': request,
               'to': receiving_client_address,
               'audio_name': audio_name,
               'audio_size': audio_size,
               'audio_format': audio_format,
               'audio_bitrate': audio_bitrate}
        packet = json.dumps(msg)
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.tcp_soc.sendall(packet)




    def get_client_list(self):
        self.tcp_soc.sendall(b'GetClintList')

        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        client_list = json.loads(buf.decode('utf-8')).get('ReplyClientList')

        print('ClientList : ', client_list)
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
