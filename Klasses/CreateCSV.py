import os
import csv
from xml.dom import minidom
from more_itertools import unique_everseen
from tkinter import ttk
from tkinter import filedialog
from difflib import SequenceMatcher
import operator


class CreateCSV:
    # save_file = ""
    file_name = ""
    dir_path = ""
    jaar =""
    boek =""

    def __init__(self, dirname,outputdir):
        self.dirname = dirname
        self.outputDir = outputdir

    def select_file(self):
        try:
            os.remove("tmp.csv")
            os.remove("straatnamen.csv")
        except:
            pass
        # self.save_file = filedialog.askdirectory(parent=self.root,initialdir="/",title='Please select a directory')
        with open(f"{self.outputDir}/tmp.csv", 'a',newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',')
            filewriter.writerow(["jaar","boek","pagina","filename","naam"])
        with open(f"{self.outputDir}/straatnamen.csv", 'a',newline='') as csvfile2:
            filewriter2 = csv.writer(csvfile2, delimiter=',')
            filewriter2.writerow(["jaar","boek","pagina","filename","straatnaam"])

        dir_path = os.listdir(self.dirname)
        for i in range(len(dir_path)):
            self.file_name = dir_path[i]
            print(f"{i}: {dir_path[i]}")
            if dir_path[i][-3:] == "xml":
                doc = minidom.parse(f"{self.dirname}/{dir_path[i]}")
                #print(doc)
                self.read_names(doc)
            else:
                print("crash op namen")
            # print(file_name)
            # read_string(doc)
            
        for i in range(len(dir_path)):
            self.file_name = dir_path[i]
            print(f"{i}: {dir_path[i]}")
            if dir_path[i][-3:] == "xml":
                doc = minidom.parse(f"{self.dirname}/{dir_path[i]}")
                #print(doc)
                self.read_streetNames(doc)
            else:
                print("crash op readnamen")
                
            # print(file_name)
            # read_string(doc)
            
        self.delete_dupes_namen(self.outputDir)
        self.delete_dupes_straatnamen(self.outputDir)

    
    def read_names(self, doc):
        strings = doc.getElementsByTagName("String")
        height = 4611
        width= 1590
        V_pos = 821
        H_pos = 194
        for string in strings:
            content_str = string.getAttribute("CONTENT")
            vpos_str = float(string.getAttribute("VPOS"))
            hpos_str = float(string.getAttribute("HPOS"))
            width_str = float(string.getAttribute("WIDTH"))
            if (vpos_str <= V_pos + height) and (vpos_str >= V_pos) and (hpos_str + width_str <= H_pos + width) and (hpos_str >= H_pos):
                try:
                    coords = float(content_str)
                except:
                    
                    contains_digit = False
                    with open('filter.txt') as f:
                        #print("open filter")
                        #print("con_str: " + content_str)
                        for letter in content_str:
                            #print("letter: " + letter)
                            if letter.isdigit():
                                contains_digit = True
                            else:
                                pass
                        
                        if content_str.lower() in f.read() or contains_digit is True:
                            pass
                        else:
                            if '"' in content_str:
                                content_str = content_str.replace('"', '')
                                # print(len(string))
                                if len(content_str) > 2:
                                    #print(string)
                                    #print("make csv now")
                                    self.make_csv(content_str , "tmp.csv", self.file_name)
                            else: 
                                #print(string)
                                #print("make csv now")
                                self.make_csv(content_str , "tmp.csv", self.file_name)
                            contains_digit = False                 
        else:
            pass
        

    def read_streetNames(self, doc):
        height = 388
        width= 4010
        V_pos = 0
        H_pos = 0
        strings = doc.getElementsByTagName("String")
        for string in strings:
            content_str = string.getAttribute("CONTENT")
            vpos_str = float(string.getAttribute("VPOS"))
            hpos_str = float(string.getAttribute("HPOS"))
            if (vpos_str <= V_pos + height) and (vpos_str >= V_pos) and (hpos_str <= H_pos + width) and (hpos_str >= H_pos):
                #print(content_str)
                try:
                    coords = float(content_str)
                    # print(crashshit)
                    #print(content_str)
                except:
                    #print(content_str)
                    no_comma = content_str.replace(',', '')
                    naam = no_comma
                    contains_digit = False
                    
                    with open('filter.txt') as f:
                        for letter in no_comma:
                            if letter.isdigit():
                                contains_digit = True
                            else:
                                pass

                        if no_comma.lower() in f.read() or contains_digit is True:
                            pass
                        else:
                            f = open("straatnamen2.csv", "r")
                            f.readline()
                            names = f.readlines()
                            NewName_percentage = {}
                            naam_percentage = {}
                            for name in names:
                                name = name.split(",")
                                name[1] = name[1].replace("\n", "")
                                if self.similar(name[1].lower(),naam.lower()) >= 0.75:
                                    try:
                                        similarity = self.similar(name[1].lower(),naam.lower())
                                        NewName_percentage[name[0]] = similarity
                                        naam_percentage[naam] = similarity 
                                    except:
                                        pass
                                elif self.similar(name[0].lower(),naam.lower()) >= 0.75:
                                    try:
                                        similarity = self.similar(name[0].lower(),naam.lower())
                                        NewName_percentage[name[0]] = similarity
                                        naam_percentage[naam] = similarity
                                    except:
                                        pass
                                else:
                                    pass
                            if naam not in naam_percentage and naam not in NewName_percentage:
                                f = open("stratenNL.txt", "r")
                                f.readline()
                                names = f.readlines()
                                for name in names:
                                    if self.similar(name[:-1].lower(),naam.lower()) >= 0.75:
                                        try:
                                            similarity = self.similar(name[:-1].lower(),naam.lower())
                                            NewName_percentage[naam] = similarity
                                            naam_percentage[naam] = similarity
                                        except:
                                            pass
                                    else:
                                        pass
                            else:
                                pass
                            try:
                                nieuwe_straatnaam = max(NewName_percentage.items(), key=operator.itemgetter(1))[0]
                                print(naam ,"-------------->" ,nieuwe_straatnaam)
                                self.make_csv(nieuwe_straatnaam, "straatnamen.csv", self.file_name)
                                contains_digit = False
                            except:
                                pass
            else:
                pass        

    def make_csv(self, cont_str, csv_name, file_name):
        # print(self.file_name[:4],self.file_name[5:7],self.file_name[8:11],self.file_name[:-4],cont_str)
        # print(file_name)

        with open(f"{self.outputDir}/{csv_name}", 'a',newline='') as csvfile:
            file_name_splitted = file_name.split("_")
            filewriter = csv.writer(csvfile, delimiter=',')
            self.jaar = file_name_splitted[1]
            self.boek = file_name_splitted[2]
            pagina = file_name_splitted[3].replace(".xml","")
            file_name = self.jaar + "_" + self.boek + "_" + pagina + ".tif"
            filewriter.writerow([self.jaar,self.boek,pagina,file_name,cont_str])
            # print("hij heeft geprint in ",f"{self.save_file}/{csv_name}" )

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def delete_dupes_straatnamen(self, save_file):
        naam2 =save_file + "/" + self.jaar+ "_" + self.boek + "_" + "straatnamen.csv"
        try:
            os.remove(naam2)
        except:
            pass
        naam = save_file + "/straatnamen.csv"
        # file_name_output = f"{save_file}/Namen_output_transkribus.csv"
        with open(naam,'r') as f, open(naam2,'w') as out_file:
            out_file.writelines(unique_everseen(f))
        try:
            os.remove(naam)
        except:
            pass

    def delete_dupes_namen(self, save_file):
        naam2 = save_file + "/" + self.jaar+ "_" +self.boek + "_" + "namen.csv"
        try:
            os.remove(naam2)
        except:
            pass
        naam = save_file + "/tmp.csv"
        # file_name_output = f"{save_file}/Namen_output_transkribus.csv"
        with open(naam,'r') as f, open(naam2,'w') as out_file:
            out_file.writelines(unique_everseen(f))
        try:
            os.remove(naam)
        except:
            pass


