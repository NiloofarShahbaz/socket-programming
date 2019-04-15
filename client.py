import socket
import json
import struct
from os import path
from threading import Thread
import mutagen
from pydub import AudioSegment
import random
import pyaudio
import time
from tkinter import *
from GUI import Window

import threading
buf_size = 1024

class Client(Thread):
    def __init__(self, host, port, sendFlag=True):
        super().__init__()
        self.sendFlag = sendFlag
        self.server_host = host
        self.server_port = port
        # self.gui = gui
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port = random.randrange(9999, 65535)
        self.tcp_soc.bind((self.server_host, port))
        self.udp_soc.bind((self.server_host, port))
        self.connected = False

    def send(self):
        root1 = Tk()
        root1.geometry("600x400")
        self.sender_window = Window(root1, "sender")

        client_list = self.get_client_list()
        while not len(client_list):
            # repeat until there's a client
            client_list = self.get_client_list()

        receiving_client_address = random.choice(client_list)
        client_answer = self.request_to_send(receiving_client_address)
        if client_answer is None:
            return
        if client_answer == 'accept':
            self.send_audio()

    def receive(self):
        audio_name, audio_format, sample_width, channels, rate = self.get_request()

        if audio_name:
            self.receive_audio(audio_name, audio_format, sample_width, channels, rate)

    def send_audio(self):
        audio = open('sample.wav', 'rb')
        data = audio.read(buf_size)
        i = 1
        while data:
            print('input', i)
            i = i+1
            if self.udp_soc.sendto(data, (self.server_host, self.server_port)):
                data = audio.read(buf_size)
                time.sleep(0.01)
        audio.close()

    def receive_audio(self, audio_name, audio_format, sample_width, channels, rate):
        audio = open(audio_name + '1.' + audio_format, 'wb')
        # wf = wave.open(audio_name + '1.' + audio_format, 'wb')
        # wf1 = wave.open(audio_name + '1.' + audio_format, 'rb')
        # wf.setnchannels(channels)
        # wf.setsampwidth(sample_width)
        # wf.setframerate(rate)
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
                # wf.writeframes(data)
                # wf1.readframes(1024)
                self.udp_soc.settimeout(1)
                data, address = self.udp_soc.recvfrom(buf_size)
        except socket.timeout:
            print('bye')
            stream.stop_stream()
            stream.close()
            audio.close()
            self.udp_soc.close()

    def request_to_send(self, receiving_client_address):
        file_path = 'sample.wav'

        request = 'RequestToSend'
        audio = open(file_path, 'rb')
        audio_name = path.basename(audio.name)
        audio_size = path.getsize(audio.name)
        audio_name, audio_format = path.splitext(audio_name)
        audio_format = audio_format[1:]
        audio.close()
        audio = mutagen.File(file_path)
        # audio_bitrate = audio.info.bitrate
        if audio_format == "mp3":
            audio = AudioSegment.from_mp3(file_path)
        elif audio_format == "wav":
            audio = AudioSegment.from_wav(file_path)
        else:
            # TODO : raise exception --> only wav or mp3 format
            audio = AudioSegment.from_file(file_path, audio_format)

        msg = {'request': request,
               'to': receiving_client_address,
               'audio_name': audio_name,
               'audio_size': audio_size,
               'audio_format': audio_format,
               # 'audio_bitrate': audio_bitrate,
               'pyaudio_sample_width': audio.sample_width,
               'pyaudio_channels': audio.channels,
               'pyaudio_framerate': audio.frame_rate
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
        print('Server -->', msg)
        if msg.get('request') == 'AcceptRequest':
            client_answer = msg.get('answer')
            return client_answer
        else:
            self.connected = False

    def get_request(self):
        self.reciver_window.sender_window('reciver : ')
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
            audio_name = msg.get('audio_name')
            audio_format = msg.get('audio_format')
            sample_width = msg.get('pyaudio_sample_width')
            channels = msg.get('pyaudio_channels')
            rate = msg.get('pyaudio_framerate')
            msg = {'request': 'AcceptRequest',
                   'answer': 'accept'
                   }
            # or deny!
            packet = json.dumps(msg).encode('utf-8')
            length = struct.pack('!I', len(packet))
            packet = length + packet
            self.tcp_soc.sendall(packet)

            return audio_name, audio_format, sample_width, channels, rate

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



