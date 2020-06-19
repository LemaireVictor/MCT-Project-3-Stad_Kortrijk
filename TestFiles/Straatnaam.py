import pandas
import os
# import xml.dom.minidom as xdm
import csv
from xml.dom import minidom
from difflib import SequenceMatcher
from more_itertools import unique_everseen


height = 388
width= 4010
V_pos = 0
H_pos = 0
file_name = ""

def select_file():
    try:
        os.remove("straatnamen.csv")
    except:
        pass
    
    with open('straatnamen.csv', 'a',newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(["jaar","boek","pagina","filename","straatnaam"])
    global file_name
    arr = os.listdir("alto/")
    for i in range(len(arr)):
        file_name = arr[i]
        #print(f"{i}: {arr[i]}")
        doc = minidom.parse(f"alto/{arr[i]}")
        # print(file_name)
        #print(doc.firstChild.tagName)
        read_string(doc)
    delete_dupes() 



def read_string(doc):
    strings = doc.getElementsByTagName("String")
    for string in strings:
        content_str = string.getAttribute("CONTENT")
        vpos_str = float(string.getAttribute("VPOS"))
        hpos_str = float(string.getAttribute("HPOS"))
        if (vpos_str <= V_pos + height) and (vpos_str >= V_pos) and (hpos_str <= H_pos + width) and (hpos_str >= H_pos):
            #print(content_str)
            try:
                crashshit = float(content_str)
                # print(crashshit)
                #print(content_str)
            except:
                #print(content_str)
                no_comma = content_str.replace(',', '')
                naam = no_comma
                with open('filter.txt') as f:
                    if no_comma.lower() in f.read():
                        pass
                    else:
                        f = open("straten.txt", "r")
                        f.readline()
                        names = f.readlines()

                        for name in names:
                            if similar(name[:-1].lower(),naam.lower()) >= 0.75:
                                sim = similar(name[:-1].lower(),naam.lower())
                                print("gevonden: " + name[:-1] + " ---- " + naam + " ---- " + str(sim))
                                make_csv(no_comma)
                                
                            else:
                                pass
        else:
            pass

    print('vaak geprint ook :////')
    # delete_dupes()
          
                
def delete_dupes():
    naam2 ="straatnamen_output_transkribus.csv"
    try:
        os.remove(naam2)
    except:
        pass
    naam = "straatnamen.csv"
    
    # file_name_output = f"{save_file}/Namen_output_transkribus.csv"
    with open(naam,'r') as f, open(naam2,'w') as out_file:
        out_file.writelines(unique_everseen(f))

    try:
        os.remove(naam)
    except:
        pass
    
    
    



         
def make_csv(cont_str):
    global file_name
    print(file_name[:4],file_name[5:7],file_name[8:11],file_name[:-4],cont_str)
    with open('Straatnamen.csv', 'a',newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow([file_name[:4],file_name[5:7],file_name[8:11],file_name[:-4],cont_str])

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()



select_file()
