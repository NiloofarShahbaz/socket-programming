import socket
from server import Server
from client import Client
from threading import Thread

host = '127.0.0.1'
port = 1041

server = Server()
client = Client(host, port)

server.start()
client.start()



