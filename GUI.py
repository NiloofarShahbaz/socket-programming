from tkinter import *


class Window(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master, name):
        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        # changing the title of our master widget
        self.master.title(name)

        self.title_font=("Helvetica", 16)
        self.button_font = ("Helvetica", 11)
        self.server_font = ("Helvetica", 14)

    # Creation of init_window
    def client_init_window(self,recive_fun,send_fun):

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a button instance
        label = Label(self, text="Choose to recive or send file", font=self.title_font)
        # label.pack()
        quitButton1 = Button(self, text="Connect as reciver", command=recive_fun, padx=10, pady=15, bg="royalblue3", font=self.button_font)
        quitButton2 = Button(self, text="Connect as sender", command=send_fun, padx=10, pady=15, bg="chartreuse3", font=self.button_font)

        # placing on my window
        label.place(x=125, y=100)
        quitButton1.place(x=205, y=155)
        quitButton2.place(x=205, y=220)


    def server_init_window(self, text):

        self.pack(fill=BOTH, expand=1)

        self.master.title("server response")

        label = Label(self, text=text, font=self.server_font)

        label.pack()


    def sender_window(self, text):

        self.pack(fill=BOTH, expand=1)

        self.master.title("server response")

        label = Label(self, text=text, font=self.server_font)

        label.pack()




