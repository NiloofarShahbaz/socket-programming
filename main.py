import socket
from server import Server
from client import Client
from threading import Thread
from tkinter import *
from GUI import Window

def sender():
    client1 = Client(server.host, server.port)
    client1.start()
    client2 = Client(server.host, server.port, False)
    client2.start()

    # for child in app.winfo_children():
    #     child.destroy()

def reciver():
    client1 = Client(server.host, server.port)
    client1.start()
    client2 = Client(server.host,  server.port, False)
    client2.start()
    # for child in app.winfo_children():
    #     child.destroy()


root = Tk()

root.geometry("600x400")

# creation of an instance
app = Window(root, "initial")

server = Server(app.server_init_window)
server.start()

app.client_init_window(reciver,sender)

# # creation of an instance
# server_app = Window(root, "server")
#
# server_app.init_window(server , "server")

# mainloop
root.mainloop()




