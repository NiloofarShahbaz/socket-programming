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

buf_size = 1024


class Client(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.server_host = host
        self.server_port = port
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_port = random.randrange(9999, 65535)
        self.tcp_soc.bind((self.server_host, self.my_port))
        self.udp_soc.bind((self.server_host, self.my_port))
        self.connected = False

    def send(self, receiving_client_address):
        file_path = raw_input(str(self.my_port) + " : input file:\n")
        client_answer = self.request_to_send(receiving_client_address, file_path)
        if client_answer is None:
            return
        if client_answer == 'accept':
            self.send_audio(file_path)

    def receive(self):
        audio_name, audio_format, sample_width, channels, rate = self.get_request()

        if audio_name:
            self.receive_audio(audio_name, audio_format, sample_width, channels, rate)

    def send_audio(self, file_path):
        # audio = open(file_path, 'rb')
        # data = audio.read(buf_size)
        # while data:
        #     if self.udp_soc.sendto(data, (self.server_host, self.server_port)):
        #         data = audio.read(buf_size)
        #         time.sleep(0.01)
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 3
        WAVE_OUTPUT_FILENAME = "output.wav"
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            self.udp_soc.sendto(data, (self.server_host, self.server_port))

        # while True:


        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def receive_audio(self, audio_name, audio_format, sample_width, channels, rate):
        # audio = open(audio_name + '1.' + audio_format, 'wb')
        WAVE_OUTPUT_FILENAME = "output_final.wav"
        frames=[]
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 5

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)
        data, address = self.udp_soc.recvfrom(buf_size)

        try:
            while data:
                # audio.write(data)
                frames.append(data)
                stream.write(data)
                self.udp_soc.settimeout(1)
                data, address = self.udp_soc.recvfrom(buf_size)
        except socket.timeout:
            print('bye')
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.udp_soc.close()
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            # audio.close()

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

        # wait for reply
        buf = b''
        while len(buf) < 4:
            buf += self.tcp_soc.recv(4 - len(buf))
        length = struct.unpack('!I', buf)[0]

        buf = b''
        while len(buf) < length:
            buf += self.tcp_soc.recv(length - len(buf))

        msg = json.loads(buf.decode('utf-8'))
        print(self.my_port, 'Server -->', msg)
        if msg.get('request') == 'AcceptRequest':
            client_answer = msg.get('answer')
            return client_answer
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
        print(self.my_port, ': Server -->', msg)

        if msg.get('request') == 'RequestToSend':
            choice = raw_input(str(self.my_port) + " : do you accept this audio?[y/n]\n")
            if choice == 'y':
                audio_name = msg.get('audio_name')
                audio_format = msg.get('audio_format')
                sample_width = msg.get('pyaudio_sample_width')
                channels = msg.get('pyaudio_channels')
                rate = msg.get('pyaudio_framerate')
                msg = {'request': 'AcceptRequest',
                       'answer': 'accept'
                       }
                packet = json.dumps(msg).encode('utf-8')
                length = struct.pack('!I', len(packet))
                packet = length + packet
                self.tcp_soc.sendall(packet)

                return audio_name, audio_format, sample_width, channels, rate
            else:
                self.connected = False
                return

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
        print(self.my_port, ': Server -->', msg)

        client_list = msg.get('ReplyClientList')

        return client_list

    def run(self):
        # while True:
        self.tcp_soc.connect((self.server_host, self.server_port))
        self.connected = True
        print(self.my_port, ": you are now connected to server")

        choice = raw_input(str(self.my_port) + ' : do you want to get the connected client list?[y/n]\n')
        flag = False
        if choice == 'y':
            client_list = self.get_client_list()
            # if no client repeat until you get one!
            while not len(client_list):
                print('-------no client-------')
                choice = input(str(self.my_port) + ' : do you want to get the connected client list?[y/n]\n')
                if choice == 'y':
                    client_list = self.get_client_list()
                elif choice == 'n':
                    flag = True
                    break

            if not flag:
                print('--------client list-------')
                for i in range(0, len(client_list)):
                    print(str(i + 1) + '.', client_list[i])

                choice = str(input(str(self.my_port) + " : which client you want to sent audio to?"
                                                   "[enter the number or enter 'n' if you don't want to]\n"))

                if choice.isalnum():
                    selected_client = client_list[int(float(choice)) - 1]
                    self.send(selected_client)

        if choice == 'n':
            print(self.my_port, "ok so wait for someone to send you request!")
            self.receive()
