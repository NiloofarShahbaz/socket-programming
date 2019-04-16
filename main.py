import socket
from server import Server
from client import Client
from threading import Thread

server = Server()
client1 = Client(server.host, server.port)
client2 = Client(server.host, server.port)
client3 = Client(server.host, server.port)
client4 = Client(server.host, server.port)

server.start()
client1.start()
client2.start()
client3.start()
client4.start()

