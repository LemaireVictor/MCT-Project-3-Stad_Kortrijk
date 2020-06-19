# --------------------imports--------------------------------------------------------------------------------
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import csv
from xml.dom import minidom
from more_itertools import unique_everseen
from Klasses.CreateCSV import CreateCSV


# --------------------open screen--------------------------------------------------------------------------------
root = Tk() 
dirname = ""
# --------------------functies tkinter--------------------------------------------------------------------------------
# show dialog + dirname
def show():
    global dirname
    delete_label()
    dirname = filedialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
    show_label(dirname)

def delete_label():
    entry_dir.delete(0, END)
def show_label(dirname):
    entry_dir.insert(0, dirname)

def convert():
    create = CreateCSV(dirname, root)
    create.select_file()




# --------------------Layout van tkinter-------------------------------------------------------------------------
Label(root, text="Naam dir:").grid(row=1, column=0)
button_Login =  Button(root, text="Open Folder", command=show)
button_Login.grid(row=4, column=0,pady=(0, 5), padx=(5, 5))

button_Login =  Button(root, text="converteer naar csv", command=convert)
button_Login.grid(row=5, column=0,pady=(0, 5), padx=(5, 5))


v = StringVar()
entry_dir = Entry(root, textvariable=v, width = 40)
entry_dir.grid(row=1, column=1, pady=(5, 5))




# --------------------configure tkinter--------------------------------------------------------------------------------
Grid.rowconfigure(root, 5, weight=1)
Grid.columnconfigure(root, 4, weight=1)
root.geometry("400x300")
root.mainloop()


# --------------------