from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
from functools import partial
from tkinter import messagebox
import Queue

class Window(Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master, name ,q):
        # parameters that you want to send through the Frame class.
        Frame.__init__(self, master)

        # reference to the master widget, which is the tk window
        self.master = master

        self.x=0
        self.queue=q

        # changing the title of our master widget
        self.master.title(name)

        self.client_answer=''

        self.title_font=("Helvetica", 16)
        self.button_font = ("Helvetica", 11)
        self.server_font = ("Helvetica", 14)
        # self.client_list_font = ("Helvetica", 14)
        s = ttk.Style()  # Creating style element
        s.configure('Helvetica') # First argument is the name of style. Needs to end with: .TRadiobutton)

    # Creation of init_window
    def init_window(self,client_fun):

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        # creating a button instance
        # label = Label(self, text="Choose to recive or send file", font=self.title_font)
        # label.pack()
        quitButton1 = Button(self, text="Connect to server", command=client_fun, padx=10, pady=15, bg="royalblue3", font=self.button_font)

        # placing on my window
        # label.place(x=125, y=100)
        quitButton1.place(x=205, y=155)


    def server_init_window(self, client_list):
        print("server gui", client_list)

        self.pack(fill=BOTH, expand=1)
        if len(client_list) > 4 :
            Lb1 = Listbox(self, height=4, width=33, fg="SpringGreen4" , font=self.button_font)
            Lb2 = Listbox(self, height=4, width=33, fg="SpringGreen4", font=self.button_font)
            for i in range(0,len(client_list)):
                if(i>len(client_list)/2):
                    Lb2.insert(i + 1, str(client_list[i][0]) + str(client_list[i][1]) + "------------ Connected")
                else:
                    Lb1.insert(i+1, str(client_list[i][0])+str(client_list[i][1])+"------------ Connected")
            Lb1.place(x=25,y=15)
            Lb2.place(x=405,y=15)

        else:
            Lb1 = Listbox(self, height=5, width=70, fg="SpringGreen4", font=self.button_font)
            for i in range(0,len(client_list)):
                Lb1.insert(i+1, str(client_list[i][0])+str(client_list[i][1])+"------------ Connected")
            Lb1.place(x=15,y=15)



        # label.pack()


    def client_window(self,client, text=None):

        self.pack(fill=BOTH, expand=1)
        if text ==None:
            label = Label(self, text="you are now connected to server", font=self.title_font, fg="SpringGreen4")
            label.pack()
        else:
            label=Label(self, text=text, font=self.title_font, fg="red")
            label.pack()
        label = Label(self, text="do you want to get the connected client list?", font=self.title_font)
        label.pack()

        quitButton1 = Button(self, text="Yes", command=client.client_list_yes, padx=51, pady=15, bg="royalblue3",
                             font=self.button_font)
        quitButton2 = Button(self, text="No", command=client.client_list_no, padx=55, pady=15, bg="royalblue3",
                             font=self.button_font)

        quitButton1.place(x=205, y=105)
        quitButton2.place(x=205, y=180)

    def show_client_list(self, client, client_list):
        var = IntVar(self)
        i = 1
        label = Label(self, text="please choose an adress for sending audio", font=self.title_font)
        label2 =Label(self, text="choose no for reciving audio", font=self.title_font)
        label.pack()
        label2.pack()
        for c in client_list:
            Radiobutton(self,
                            text=c,
                            variable=var,
                            value=i,
                            indicatoron=0,
                            width=50,
                            font=self.server_font,
                            bg='lavender',
                            command=partial(client.client_list_choice, var)).pack(anchor=W)
            i = i + 1

        Radiobutton(self,
                        text='No',
                        variable=var,
                        value=0,
                        indicatoron=0,
                        width=50,
                        font=self.server_font,
                        bg='lavender',
                        command=partial(client.client_list_choice, var)).pack(anchor=W)





    def ShowChoice(self, var ,client):
        print("selected",var.get())



    def getting_request(self):
        label = Label(self, text="please wait for the other client to send request", font=self.server_font, fg='royalblue3')
        label.place(x=70,y=150)


    def alert_request(self, msg, client):

        ans=messagebox.askquestion("Request Information", "client "+str(msg.get('from'))+" wants to send an audio with name "+
                            str(msg.get('audio_name'))+" and size "+ str(msg.get('audio_size')) + " ,Do you want to recive it?")

        if ans == 'yes':
            client.accept_req()

        else:
            client.decline_req()

    def sending_audio(self,size,text):
        label = Label(self, text=text, font=self.server_font,
                      fg='SpringGreen4')
        label.place(x=150,y=85)
        self.send_size=size
        self.progress=ttk.Progressbar(self,
                        orient='horizontal',
                        mode='determinate',
                        length=460,
                        maximum=size)
        self.progress.place(x=100, y=130)
        self.progress.start(6)

    def sending_progress(self, i):

        self.progress.step(i)
        if i==self.send_size:
            self.progress1.stop()


    def reciving_audio(self,size,text):
        label = Label(self, text=text, font=self.server_font,
                      fg='SpringGreen4')
        self.recive_size=size
        label.place(x=150,y=85)
        self.progress1=ttk.Progressbar(self,
                        orient='horizontal',
                        mode='determinate',
                        length=460,
                        maximum=size)
        self.progress1.place(x=100, y=130)
        self.progress1.start(6)


    def reciving_progress(self, i):
        print("hello")
        self.progress1.step(i)
        if i==self.recive_size:
            self.progress1.stop()


    def finish_sending(self, text):
        print("hello")
        # label = Label(self, text="successfully sent!", font=self.server_font,
        #               fg='SpringGreen4')
        # label.pack()
        messagebox.showinfo("Success", "file "+text + " successfuly")

    def server_warning(self):
        messagebox.showwarning("Warning", "TCP Thread did not start.")

    def server_messages(self, msg, address, to=None):
        if address!='server':
            label = Label(self, text="client "+str(address) + " :", font=self.server_font,
                          fg='royalblue3')
        else:
            if to ==None:
                label = Label(self, text="server reply" + " :", font=self.server_font,
                            fg='royalblue3')
            else:
                label = Label(self, text="server reply to " +str(to) + " :", font=self.server_font,
                              fg='royalblue3')
        label2 = Label(self, text=msg, font=self.server_font,
                      fg='slate gray')

        label.place(x=15, y=150 + self.x * 30)
        if to==None:
            label2.place(x=180, y=150 + self.x * 30)
            self.x = self.x + 1
        else:
            label2.place(x=15 , y=180+self.x*30)
            self.x = self.x + 2