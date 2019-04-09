import socket
from server import Server
from client import Client
from threading import Thread

server = Server()
client1 = Client(server.host, server.port)
client2 = Client(server.host, server.port, False)

server.start()
client1.start()
client2.start()


