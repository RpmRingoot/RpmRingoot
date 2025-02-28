#!/usr/bin/python3
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import paho.mqtt.client as mqtt
import serial

from PIL import Image as pil
from pkg_resources import parse_version

if parse_version(pil.__version__)>=parse_version('10.0.0'):
    Image.ANTIALIAS=Image.LANCZOS


class MQTTTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MQTT Tabellen met Tkinter")
        # Load the icon image using PIL
        icon = Image.open("klein-ris.png")
        icon = ImageTk.PhotoImage(icon)
        # Set the taskbar icon
        self.root.iconphoto(True, icon)
        
        self.max_rows_topic1 = 8    #opstart instelling
        self.max_rows_topic2 = 6    #opstart instelling
        self.data_topic1 = []
        self.data_topic2 = []

        # MQTT Client instellen
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect("192.168.2.8")#"mqtt.eclipseprojects.io")
        self.client.subscribe("topic1")
        self.client.subscribe("topic2")
        self.client.loop_start()
        
        # Frame voor interface
        self.frame = tk.Frame(root)
        self.root.geometry("700x700")
        self.root.resizable(False, False)
        self.frame.pack()
        
        # Plaatje in de linker bovenhoek
        self.load_image()
        
        # Schuifregelaars
        self.slider1 = tk.Scale(self.frame, from_=1, to=10, orient="horizontal",bd=3,length=210,tickinterval=2,activebackground='white', foreground='red',troughcolor="red",fg="red",font=("Arial", 12, "bold"),label="Aantal regels in Rooier",
                                command=self.update_max_rows_topic1)
        self.slider1.set(self.max_rows_topic1)
        self.slider1.grid(row=0, column=1, padx=10, pady=5)


        # Schuifregelaar 2        
        self.slider2 = tk.Scale(self.frame, from_=1, to=10, orient="horizontal",bd=3,length=210,tickinterval=2,fg='green',activebackground='white',troughcolor="green",font=("Arial", 12, "bold"),label="Aantal regels RassenLijst",
                                command=self.update_max_rows_topic2)
        self.slider2.set(self.max_rows_topic2)
        self.slider2.grid(row=0, column=2, padx=10, pady=5)
        
        # Tabellen
        self.tree1 = self.create_table("Aardappel Rassen in de Rooier")
        self.tree2 = self.create_table("RassenLijst")


        # Knoppen
        self.print_button = tk.Button(self.frame, text="Print bovenste rij uit Rassenlijst",bd=5,activebackground='yellow', command=self.print_serial)
        self.print_button.grid(row=2, column=2, padx=10, pady=5)
    
    def load_image(self):
        try:
            image = Image.open("klein-ris.png")
            image = image.resize((200, 100), Image.ANTIALIAS)
            self.photo = ImageTk.PhotoImage(image)
            self.image_label = tk.Label(self.frame, image=self.photo)
            self.image_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
        except Exception as e:
            print("Fout bij laden afbeelding:", e)

    def create_table(self, title):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)
        label = ttk.Label(frame, text=title, foreground='black', font=("Arial", 14, "bold"))
        #label = ttk.Label(frame, text=title, background='red', foreground='red', font=("Arial", 14, "bold"))
        label.pack()
        
        tree = ttk.Treeview(frame, columns=("#1",), show='headings')
        tree.heading("#1", text="Received Data")
        #self.tree2.heading("#1", text="Data")
        tree.column("#1", width=650)
        tree.pack(padx=10,pady=10)
        return tree

    def update_max_rows_topic1(self, value):
        self.max_rows_topic1 = int(value)
        self.refresh_table(self.tree1, self.data_topic1, self.max_rows_topic1)

    def update_max_rows_topic2(self, value):
        self.max_rows_topic2 = int(value)
        self.refresh_table(self.tree2, self.data_topic2, self.max_rows_topic2)
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8").ljust(75)[:75]
        
        if topic == "topic1":
            self.data_topic1.append(payload)
            if len(self.data_topic1) > self.max_rows_topic1:
                self.data_topic1.pop(0)
            self.refresh_table(self.tree1, self.data_topic1, self.max_rows_topic1)
        elif topic == "topic2":
            self.data_topic2.append(payload)
            if len(self.data_topic2) > self.max_rows_topic2:
                self.data_topic2.pop(0)
            self.refresh_table(self.tree2, self.data_topic2, self.max_rows_topic2)
            #self.print()
            self.print_serial()  # Automatisch printen na update
    
    def refresh_table(self, tree, data, max_rows):
        tree.delete(*tree.get_children())
        for item in data[-max_rows:]:
            tree.insert("", "end", values=(item,))
    
    def print_serial(self):
        if self.data_topic2:
            top_value = self.data_topic2[0]
            try:
                with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
                    ser.write((top_value + "\n").encode('utf-8'))
            except Exception as e:
                print("Seriële fout:", e)



if __name__ == "__main__":
    root = tk.Tk()
    app = MQTTTableApp(root)
    root.mainloop()

