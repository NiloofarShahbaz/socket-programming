import socket
import json
import struct
from os import path
from threading import Thread
import random
import pyaudio
import time
from tkinter import *
from GUI import Window
import wave
import threading
from tkinter import filedialog

buf_size = 1024


class Client(Thread):
    def __init__(self, host, port, id, root):
        super().__init__()
        self.server_host = host
        self.server_port = port
        # self.gui = gui
        self.choice =''
        self.request_ans=''
        self.client_address_choice=''
        self.root=root
        self.tcp_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.my_port = random.randrange(9999, 65535)
        self.tcp_soc.bind((self.server_host, self.my_port))
        self.udp_soc.bind((self.server_host, self.my_port))
        self.connected = False
        self.id = id

    def send(self,receiving_client_address):
        self.sender_window.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("wav files","*.wav"),("all files","*.*")))
        print ("addreess",self.sender_window.filename)

        # file_path = input(str(self.my_port) + " : input file:\n")
        client_answer = self.request_to_send(receiving_client_address, self.sender_window.filename)
        # self.sender_window.sender_choose_client_window()
        if client_answer is None:
            return
        if client_answer == 'accept':
            self.send_audio(self.sender_window.filename)
            for child in self.sender_window.winfo_children():
                child.destroy()
            self.sender_window.finish_sending("sent")


    def receive(self):
        # root1 = Tk()
        # root1.geometry("600x400")
        # self.reciver_window = Window(root1, "reciver")
        # self.reciver_window.reciver_init_winodw()
        audio_name, audio_format, sample_width, channels, rate = self.get_request()


        if audio_name:
            self.receive_audio(audio_name, audio_format, sample_width, channels, rate)
            self.sender_window.finish_sending("received")

        # root1.mainloop()
    def send_audio(self, file_path):
        audio = open(file_path, 'rb')
        audio_size = path.getsize(audio.name)
        data = audio.read(buf_size)
        i=0
        for child in self.sender_window.winfo_children():
            child.destroy()
        self.sender_window.sending_audio(audio_size,"Sending File")
        while data:
            if self.udp_soc.sendto(data, (self.server_host, self.server_port)):
                i = i+1
                self.sender_window.sending_progress(buf_size)
                data = audio.read(buf_size)
                time.sleep(0.01)
        audio.close()

    def receive_audio(self, audio_name, audio_format, sample_width, channels, rate):
        audio = open(audio_name + '1.' + audio_format, 'wb')
        audio_size = path.getsize(audio.name)
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(sample_width),
                        channels=channels,
                        rate=rate,
                        output=True,
                        frames_per_buffer=buf_size)
        data, address = self.udp_soc.recvfrom(buf_size)
        i = 0
        for child in self.sender_window.winfo_children():
            child.destroy()
        # self.sender_window.reciving_audio(audio_size,"Reciving File")
        try:
            while data:
                print("hey?")
                audio.write(data)
                stream.write(data)
                i = i + 1
                # self.sender_window.reciving_progress(buf_size)
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
        # self.reciver_window.sender_window('reciver : ')
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
            # choice = input(str(self.my_port) + " : do you accept this audio?[y/n]\n")
            self.sender_window.alert_request(msg, self)

            while True:
                if self.request_ans != '':
                    break

            if self.request_ans == 'y':
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
        root1 = Toplevel(self.root)
        root1.wm_geometry("600x400")
        self.sender_window = Window(root1, "client")
        self.tcp_soc.connect((self.server_host, self.server_port))
        self.connected = True
        print(self.my_port, ": you are now connected to server")
        self.sender_window.client_window(self)

        while True:
            if self.choice !='':
                break

        for child in self.sender_window.winfo_children():
            child.destroy()

        # choice = input(str(self.my_port) + ' : do you want to get the connected client list?[y/n]\n')
        flag = False
        if self.choice == 'y':
            self.choice = ''
            client_list = self.get_client_list()
            # if no client repeat until you get one!
            while not len(client_list):
                print('-------no client-------')
                self.sender_window.client_window(self,'-------no client-------')
                while True:
                    if self.choice != '':
                        break
                # choice = input(str(self.my_port) + ' : do you want to get the connected client list?[y/n]\n')
                if self.choice == 'y':
                    self.choice = ''
                    client_list = self.get_client_list()
                elif self.choice == 0:
                    flag = True
                    break

            if not flag:
                self.sender_window.show_client_list(self, client_list)
                while True:
                    if self.client_address_choice != '':
                        break
                print('--------client list-------' ,self.client_address_choice)
                # for i in range(0, len(client_list)):
                #     print(str(i + 1) + '.', client_list[i])

                # choice = input(str(self.my_port) + " : which client you want to sent audio to?"
                #                                    "[enter the number or enter 'n' if you don't want to]\n")

                if int(self.client_address_choice) > 0:
                    selected_client = client_list[int(self.client_address_choice) - 1]
                    self.send(selected_client)

                else:
                    self.choice=0
                self.client_address_choice=''

        for child in self.sender_window.winfo_children():
            child.destroy()

        if self.choice == 0:
            self.sender_window.getting_request()
            self.choice = ''
            print(self.my_port, "ok so wait for someone to send you request!")
            self.receive()



    def client_list_yes(self):
        print("here")
        self.choice='y'

    def client_list_no(self):
        self.choice = 0

    def accept_req(self):
        self.request_ans='y'

    def decline_req(self):
        self.request_ans='n'

    def client_list_choice(self, var):
        self.client_address_choice = var.get()
