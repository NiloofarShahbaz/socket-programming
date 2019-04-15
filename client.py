import socket
import json
import struct
import random
from os import path
from threading import Thread
import mutagen
from tkinter import *
from GUI import Window



class Client(Thread):
    def __init__(self, host, port, sendFlag=True):
        super().__init__()
        self.sendFlag = sendFlag
        self.server_host = host
        self.server_port = port
        # self.gui = gui
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.tcp_soc.connect((host, port))
        print('Connected to server')

    def send(self):
        root1 = Tk()
        root1.geometry("600x400")
        self.sender_window = Window(root1, "sender")

        client_list = self.get_client_list()
        if len(client_list):
            receiving_client_address = random.choice(client_list)
            self.request_to_send(receiving_client_address)

        root1.mainloop()

    def recive(self):
        root1 = Tk()
        root1.geometry("600x400")
        self.reciver_window = Window(root1, "reciver")

        self.get_request()

        root1.mainloop()

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
        self.sender_window.sender_window('sender : ')
        print(audio_format, audio_name, audio_size, audio_bitrate)
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
        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        client_answer = json.loads(buf.decode('utf-8')).get('answer')
        print("answer",client_answer)

        return client_answer


    def get_request(self):
        self.reciver_window.sender_window('reciver : ')
        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))
        client_request = json.loads(buf.decode('utf-8'))

        print('ClientRequest : ', client_request)
        msg = {'request': 'RequestAnswer',
               'answer': 'accept',
               'to': client_request.get('from')}
        packet = json.dumps(msg).encode('utf-8')
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.tcp_soc.sendall(packet)
        return client_request


    def get_client_list(self):
        # self.tcp_soc.sendall(b'GetClintList')
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
        client_list = json.loads(buf.decode('utf-8')).get('ReplyClientList')

        print('ClientList : ', client_list)
        return client_list

    def run(self):
        if self.sendFlag:
            self.send()

        else:
            self.recive()

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
