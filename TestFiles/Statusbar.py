
# importing tkinter module 
from tkinter import * 
from tkinter.ttk import *
import time  
# creating tkinter window 
root = Tk() 

# Progress bar widget 
progress = Progressbar(root, orient = HORIZONTAL, length = 200, mode = 'determinate') 
  

def funvtion1():
    print("1 begint")
    bar()
    time.sleep(5)
    funvtion2()

def funvtion2():
    print("2 begint")
    bar()
    time.sleep(5)
    print("2 done")
    funvtion3()

def funvtion3():
    print("3 begint")
    bar()
    time.sleep(5)
    print("3 done")
    print("klaar")
# Functifon responsible for the updation 
# of the progress bar value 
def bar():
    import time 
    progress['value'] += 33
    root.update_idletasks() 
    time.sleep(1) 



progress.pack(pady = 10) 
  
# This button will initialize 
# the progress bar 
Button(root, text = 'Start', command = funvtion1).pack(pady = 10) 
  
# infinite loop 
mainloop() 