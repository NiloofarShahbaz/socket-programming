from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from functools import partial

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
        s = ttk.Style()  # Creating style element
        s.configure('Helvetica') # First argument is the name of style. Needs to end with: .TRadiobutton)

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


    def server_init_window(self, client_list):
        print("server gui")

        # self.pack(fill=BOTH, expand=1)
        # self.grid(column=0, row=0, sticky='nsew')
        # img = ImageTk.PhotoImage(Image.open("client.jpg"))
        # for i in range(0,len(client_list)):
        #     image_label = Label(image=img).grid(column=0,row=i+1)
        # ttk.Separator(self, orient='horizontal').grid(column=0,row=1, columnspan=4, sticky='ew')



        # label.pack()


    def sender_choose_client_window(self, client_list):

        self.pack(fill=BOTH, expand=1)

        var = IntVar(self)
        # var.set(0)

        # separatore.pack()
        # self.master.title("sende")
        label = Label(self, text="Choose a client to send file", font=self.title_font)
        label.pack()
        # label.pack()
        i=1
        for client in client_list:
            ttk.Radiobutton(self,
                           text=client,
                           variable=var,
                           value=i,
                           command=partial(self.ShowChoice,var)).pack(anchor=W)
            i= i+1




    def ShowChoice(self,var):
        print("selected",var.get())


    def reciver_init_winodw(self):
        label = Label(self, text="please wait for the other client to send request", font=self.title_font)
        label.pack()


    def getting_reuest(self):
        pass