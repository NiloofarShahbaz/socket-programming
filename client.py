import socket
import json
import struct
from os import path
from threading import Thread
import random
import pyaudio
import time
import wave
import threading
import traceback

buf_size = 1024


class Client(Thread):
    def __init__(self, host, port):
        super().__init__()
        self.server_host = host
        self.server_port = port
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_port = random.randrange(9999, 65535)
        self.tcp_soc.bind((self.server_host, self.my_port))
        self.udp_soc.bind((self.server_host, self.my_port))
        self.connected = False
        self.state = 0
        self.ready = False
        self.message = {}

    def send(self, receiving_client_address):
        self.state = 2
        file_path = input(str(self.my_port) + " : input file:\n")
        self.request_to_send(receiving_client_address, file_path)
        client_answer = self.handle_receive_tcp()
        if client_answer is None:
            return
        if client_answer == 'accept':
            self.send_audio(file_path)

    def receive(self):
        self.state = 3
        data = self.handle_receive_tcp()
        while data is None:
            data = self.handle_receive_tcp()
        audio_name, audio_format, sample_width, channels, rate = data
        self.get_request()

        if audio_name:
            self.receive_audio(audio_name, audio_format, sample_width, channels, rate)

    def send_audio(self, file_path):
        audio = open(file_path, 'rb')
        data = audio.read(buf_size)
        while data:
            if self.udp_soc.sendto(data, (self.server_host, self.server_port)):
                data = audio.read(buf_size)
                time.sleep(0.01)
        audio.close()

    def receive_audio(self, audio_name, audio_format, sample_width, channels, rate):
        audio = open(audio_name + '1.' + audio_format, 'wb')

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(sample_width),
                        channels=channels,
                        rate=rate,
                        output=True,
                        frames_per_buffer=buf_size)
        data, address = self.udp_soc.recvfrom(buf_size)

        try:
            while data:
                audio.write(data)
                stream.write(data)
                self.udp_soc.settimeout(1)
                data, address = self.udp_soc.recvfrom(buf_size)
        except socket.timeout:
            print('bye')
            stream.stop_stream()
            stream.close()
            audio.close()
            self.udp_soc.close()

    def request_to_send(self, receiving_client_address, file_path):

        request = 'RequestToSend'
        audio = open(file_path, 'rb')
        audio_name = path.basename(audio.name)
        audio_size = path.getsize(audio.name)
        audio_name, audio_format = path.splitext(audio_name)
        audio_format = audio_format[1:]
        audio.close()
        audio = wave.open(file_path, 'rb')
        sample_width = audio.getsampwidth()
        channels = audio.getnchannels()
        frame_rate = audio.getframerate()

        msg = {'request': request,
               'to': receiving_client_address,
               'audio_name': audio_name,
               'audio_size': audio_size,
               'audio_format': audio_format,
               'pyaudio_sample_width': sample_width,
               'pyaudio_channels': channels,
               'pyaudio_framerate': frame_rate
               }
        packet = json.dumps(msg).encode('utf-8')
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.tcp_soc.sendall(packet)

    def get_request(self):
        choice = input(str(self.my_port) + " : do you accept this audio?[y/n]\n")
        if choice == 'y':
            msg = {'request': 'AcceptRequest',
                   'answer': 'accept'
                   }
            packet = json.dumps(msg).encode('utf-8')
            length = struct.pack('!I', len(packet))
            packet = length + packet
            self.tcp_soc.sendall(packet)
            return True
        else:
            self.connected = False
            return False

    def get_client_list(self):
        msg = {'request': 'GetClintList'}
        packet = json.dumps(msg).encode('utf-8')
        length = struct.pack('!I', len(packet))
        packet = length + packet
        self.tcp_soc.sendall(packet)

    def get_tcp(self):
        while True:
            buf = b''
            while len(buf) < 4:
                buf += self.tcp_soc.recv(4 - len(buf))
            length = struct.unpack('!I', buf)[0]

            buf = b''
            while len(buf) < length:
                buf += self.tcp_soc.recv(length - len(buf))
            self.message = json.loads(buf.decode('utf-8'))
            print(self.my_port, ': Server -->', self.message)
            self.ready = True

            if 'AutoClientList' in self.message:
                client_list = self.message.get('AutoClientList')
                print('--------Auto client list-------')
                for i in range(0, len(client_list)):
                    print(str(i + 1) + '.', client_list[i])
                self.ready = False

    def handle_receive_tcp(self):
        while not self.ready:
            pass

        print('fkhdjkhk', self.message)

        if 'ReplyClientList' in self.message and self.state is 1:
            client_list = self.message.get('ReplyClientList')
            self.ready = False
            return client_list

        elif 'request' in self.message:
            if self.message.get('request') == 'AcceptRequest' and self.state is 2:
                client_answer = self.message.get('answer')
                self.ready = False
                return client_answer

            elif self.message.get('request') == 'RequestToSend' and self.state is 3:
                audio_name = self.message.get('audio_name')
                audio_format = self.message.get('audio_format')
                sample_width = self.message.get('pyaudio_sample_width')
                channels = self.message.get('pyaudio_channels')
                rate = self.message.get('pyaudio_framerate')
                self.ready = False
                return audio_name, audio_format, sample_width, channels, rate
        else:
            self.ready = False
            self.connected = False

    def run(self):
        self.tcp_soc.connect((self.server_host, self.server_port))
        self.connected = True
        print(self.my_port, ": you are now connected to server")

        try:
            Thread(target=self.get_tcp).start()
        except:
            print("Auto client list Thread did not start.")
            traceback.print_exc()

        choice = input(str(self.my_port) + ' : do you want to get the connected client list?[y/n]\n')
        flag = False
        if choice == 'y':
            self.state = 1
            self.get_client_list()
            client_list = self.handle_receive_tcp()

            # if no client repeat until you get one!
            while not len(client_list):
                print('-------no client-------')
                choice = input(str(self.my_port) + ' : do you want to get the connected client list?[y/n]\n')
                if choice == 'y':
                    self.get_client_list()
                    client_list = self.handle_receive_tcp()
                elif choice == 'n':
                    flag = True
                    break

            if not flag:
                print('--------client list-------')
                for i in range(0, len(client_list)):
                    print(str(i + 1) + '.', client_list[i])

                choice = input(str(self.my_port) + " : which client you want to sent audio to?"
                                                   "[enter the number or enter 'n' if you don't want to]\n")

                if choice.isalnum():
                    selected_client = client_list[int(float(choice)) - 1]
                    self.send(selected_client)

        if choice == 'n':
            print(self.my_port, "ok so wait for someone to send you request!")
            self.receive()
