import pandas
import os
# import xml.dom.minidom as xdm
import csv
from xml.dom import minidom


height = 4611
width= 1590
V_pos = 821
H_pos = 194
file_name = ""

def select_file():
    try:
        os.remove("namen.csv")
    except:
        pass
    
    with open('namen.csv', 'a',newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(["jaar","boek","pagina","filename","tekst"])
    global file_name
    arr = os.listdir("alto/")
    for i in range(len(arr)):
        file_name = arr[i]
        print(f"{i}: {arr[i]}")
        doc = minidom.parse(f"alto/{arr[i]}")
        # print(file_name)
        # print(doc.firstChild.tagName)
        read_string(doc)

def read_string(doc):
    strings = doc.getElementsByTagName("String")
    # print(string)
    # vpos_str = string.getAttribute("VPOS")
    # hpos_str = string.getAttribute("HPOS")
    # content_str = string.getAttribute   ("CONTENT")
    # content_str = string.attributes["CONTENT"].value
    for string in strings:
        content_str = string.getAttribute("CONTENT")
        vpos_str = float(string.getAttribute("VPOS"))
        hpos_str = float(string.getAttribute("HPOS"))
        # print(content_str, vpos_str, hpos_str)
        if (vpos_str <= V_pos + height) and (vpos_str >= V_pos) and (hpos_str <= H_pos + width) and (hpos_str >= H_pos):
            # print(content_str)
            try:
                crashshit = float(content_str)
                # print(content_str)
                # print(int(content_str)
            except ValueError as e:
                print(content_str)
                make_csv(content_str)    
                
        else:
            pass

def make_csv(cont_str):
    global file_name
    print(file_name[:4],file_name[5:7],file_name[8:11],file_name[:-4],cont_str)
    with open('namen.csv', 'a',newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow([file_name[:4],file_name[5:7],file_name[8:11],file_name[:-4],cont_str])



select_file()
