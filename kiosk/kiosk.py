from tkinter import *
from ble.ble import startBLE, startConnection
import tkinter.ttk
from PIL import ImageTk, Image
from card import readCard
from threading import *
from subprocess import *
import os
import asyncio
import time
import pickle
import queue
import copy
from builtins import bytes

from utils import remove_spaces

CC_name = ""
CC_ID = ""

devices = {}

listbox = Listbox

TIME = 10

process = None

client = None

scan = Frame

def ble_scan():
    global process
    startBLE()

def ble_updater(scan_thread):
    scan_thread.join() #needs to wait for the other thread to finish and create the devices.p file
    updateListBox()

####################################
########### PROCESS BAR ############
####################################
process_flag = 0
process = None

def bar():
    global process_flag
    global progress
    initial_value = 0
    increasing = 1
    progress.grid(pady=(20, 0))
    while(process_flag):
        if(initial_value == 100):
            increasing = 0
        elif(initial_value == 0):
            increasing = 1

        if(increasing):
            initial_value += 20
        else:
            initial_value-=20
        progress['value'] = initial_value
        root.update_idletasks()
        time.sleep(0.3)
    progress.grid_remove()


class AsyncProgress(Thread):
    def __init__(self):
        super().__init__()


    def run(self):
        bar()


####################################
############ CC READER #############
####################################

class AsyncReader(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        global process_flag
        process_flag = 1
        info = readCard().decode("utf-8") #in bytes
        info = info[:-2]
        if(info != "null"):
            info = info[:-2]    #remove \r\n
            fields = info.split('|')
            CC_name = fields[0]
            CC_ID = fields[1]
            print(fields)
        else:
            print("introduce the citizen card")
            #SHOW INFORMATION ON SCREEN TO INTRODUCE CITIZEN CARD
        process_flag = 0

def CC_click():
    read_thread = AsyncReader()
    read_thread.start()
    #process_thread = AsyncProgress()
    #process_thread.start()


def updateListBox():
    """Reads the devices.p binary file and updated the listbox with the scanned devices"""
    print("starting updater")
    global devices
    size=0
    try:
        devices = pickle.load(open("./devices.p", "rb"))
    except FileNotFoundError as e:
        print(e)
    print(devices)
    size = len(devices)
    client.updateListbox()

###############################################################

def ble_process():
    """Create and run 2 threads responsible for BLE scanning"""

    #Thread responsible for scanning devices and storing them in the devices.p binary file
    scanThread = Thread(target=ble_scan)
    scanThread.start()

    #Thread responsible for reading the devices.p file and updating the GUI with the scanned devices
    thread2 = Thread(target=ble_updater, kwargs=dict(scan_thread=scanThread))
    thread2.start()

def connectToDevice():
    active_name = listbox.get(ACTIVE)
    for mac, name in devices.items():
        if(name == active_name):
            response = startConnection(mac)
            bytes_string = bytes.fromhex(remove_spaces(response))
            ascii_string = bytes_string.decode("ASCII")
            print(ascii_string)

def createConnectingThread():
    thread1 = Thread(target=connectToDevice)
    thread1.start()

def scanWindow():
    global client
    client.destroy()
    client.endApplication()
    
    scan = Frame(root, height=800, width=480)
    client = ThreadedClient_Scan(scan)

    scan.after(1000, ble_process)
    scan.mainloop()


class GuiPart_Main:
    def __init__(self, main, queue, endCommand):
        self.queue = queue
        self.main = main
        #Setup the GUI

        main.configure(bg='#ffffff')
        main.columnconfigure(0, weight=1)
        main.grid()

        self.icon_img = PhotoImage(file='images/surething.png')
        self.icon_img = self.icon_img.zoom(25)
        self.icon_img = self.icon_img.subsample(32)

        image_label = Label(main, image=self.icon_img)
        image_label.configure(bg='#ffffff')
        image_label.grid()

        surething = Label(main, text="SureThing", fg="#EC2444", bg='#ffffff', font=("Arial", 20))
        surething.grid(pady=(10, 0))

        welcome_label = Label(main, text="Welcome!", fg="black", bg='#ffffff', font=("Arial", 20))
        welcome_label.grid(pady=(10, 0))

        auth_label = Label(main, text="Please authenticate yourself through one of the following methods",
                            fg="black", bg='#ffffff', font=("Arial", 15))
        auth_label.grid(pady=(10, 0))


        cc_label = Label(main, text="1.Introduce your Citizen Card in the Smart Card Reader",
                            fg="black", bg='#ffffff', font=("Arial", 15))
        cc_label.grid(pady=(10, 0))

        self.cc_photo = PhotoImage(file='images/cc.png').subsample(8)
        self.cc_button = Button(main, image=self.cc_photo, bg="#D3D3D3", command=CC_click)
        self.cc_button.grid(pady=(10, 10))

        progress_cc = tkinter.ttk.Progressbar(main, orient = HORIZONTAL,
                    length = 100, mode='indeterminate')

        wearable_label = Label(main, text="2.Connect through Bluetooth using a wearable device",
                            fg="black", bg='#ffffff', font=("Arial", 15))
        wearable_label.grid(pady=(10, 0))

        wearable_button = Button(main, pady=5, padx=5, text="Start Scanning!", command=scanWindow, bg="#D3D3D3", font=("Arial", 15))
        wearable_button.grid(pady=(10, 10))

        progress_ble = tkinter.ttk.Progressbar(main, orient = HORIZONTAL,
                    length = 100, mode='indeterminate')

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                function = self.queue.get(0)
                print(function)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def destroy(self):
        self.main.destroy()

class ThreadedClient_Main:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart_Main(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def workerThread1(self, function):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following two lines with the real
            # thing.
            #time.sleep(rand.random(  ) * 1.5)
            #msg = rand.random(  )
            self.queue.put(function)

    def endApplication(self):
        self.running = 0

    def destroy(self):
        self.gui.destroy()


class GuiPart_Scan:
    def __init__(self, scan_window, queue, endCommand):
        self.queue = queue
        self.main = scan_window
        #Setup the GUI
        global listbox
        scan_window.configure(bg='#ffffff')
        scan_window.columnconfigure(0, weight=1)
        scan_window.pack(fill="both", expand=True)

        self.icon_img = PhotoImage(file='images/surething.png')
        self.icon_img = self.icon_img.zoom(25)
        self.icon_img = self.icon_img.subsample(32)

        image_label_scan = Label(scan_window, image=self.icon_img)
        image_label_scan.configure(bg='#ffffff')
        image_label_scan.grid()

        surething_scan = Label(scan_window, text="SureThing", fg="#EC2444", bg='#ffffff', font=("Arial", 20))
        surething_scan.grid(pady=(10, 0))

        select_scan = Label(scan_window, text="Select your device", fg="black", bg='#ffffff', font=("Arial", 20))
        select_scan.grid(pady=(10, 0))

        listbox = Listbox(scan_window, bg='#ffffff', font=("Arial", 16), height=8)
        listbox.grid(pady=(10, 0))
        
        confirm_button = Button(scan_window, pady=5, padx=5, text="Confirm device", command=createConnectingThread, bg="#D3D3D3", font=("Arial", 15))
        confirm_button.grid(pady=(10, 10))
        
        re_scan_label = Label(scan_window, text="Your device not showing?", fg="black", bg='#ffffff', font=("Arial", 14))
        re_scan_label.place(x=root.winfo_width()-225, y=root.winfo_height()-250)
        
        rescan_button = Button(scan_window, pady=5, padx=5, text="Scan again", command=ble_process, bg="#D3D3D3", font=("Arial", 15))
        rescan_button.place(x=root.winfo_width()-180, y=root.winfo_height()-210)


    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                function = self.queue.get(0)
                print(function)
                # Check contents of message and do whatever is needed. As a
                # simple test, print it (in real life, you would
                # suitably update the GUI's display in a richer fashion).
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def destroy(self):
        self.main.destroy()
        
    def updateListbox(self):
        print("updateListbox")
        for i in devices.values():
            listbox.insert(listbox.size(), i)

class ThreadedClient_Scan:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self, master):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart_Scan(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def bleWorkerThread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """

        # To simulate asynchronous I/O, we create a random number at
        # random intervals. Replace the following two lines with the real
        # thing.
        #time.sleep(rand.random(  ) * 1.5)
        #msg = rand.random(  )
        #self.queue.put(globals()[str(function)]())
        global process
        process = Popen(["python3",  "ble/ble.py"])

    def updaterWorkerThread(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """

        # To simulate asynchronous I/O, we create a random number at
        # random intervals. Replace the following two lines with the real
        # thing.
        #time.sleep(rand.random(  ) * 1.5)
        #msg = rand.random(  )
        updateListBox()
        

    def endApplication(self):
        self.running = 0

    def destroy(self):
        self.gui.destroy()
        
    def updateListbox(self):
        self.gui.updateListbox()

if __name__ == '__main__':
    global root
    root = Tk()
    
    root.configure(bg='#ffffff')
    root.title('SureThing Kiosk')
    #root.iconbitmap('images/surething.ico')
    root.columnconfigure(0, weight=1)
    root.geometry('800x480')
    main = Frame(root, height=800, width=480)

    client = ThreadedClient_Main(main)

    main.mainloop()
