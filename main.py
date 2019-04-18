import socket
from server import Server
from client import Client
from threading import Thread
from tkinter import *
from GUI import Window
# import Queue

def client():
    global id
    global root
    client1 = Client(server.host, server.port,id,root)
    client1.start()
    id = id + 1


root = Tk()
root.geometry("600x400")

# creation of an instance
app = Window(root, "initial")
server = Server(root)
server.start()
id = 1
app.init_window(client)

# mainloop
root.mainloop()




