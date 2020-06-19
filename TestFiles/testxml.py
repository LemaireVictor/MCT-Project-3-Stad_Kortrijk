import csv


file_name = "0001_1880_02_001.xml"
filename2 = "0001_1881_2_001.xml"


with open("test.csv", 'a',newline='') as csvfile:
    file_name_splitted = filename2.split("_")
    filewriter = csv.writer(csvfile, delimiter=',')
    jaar = file_name_splitted[1]
    boek = file_name_splitted[2]
    pagina = file_name_splitted[3].replace(".xml","")
    file_name = jaar + "_" + boek + "_" + pagina + ".tif"
    filewriter.writerow([jaar,boek,pagina,file_name,cont_str])



txt = "welcome, to, the, jungle"

x = file_name.split("_")
x = x[2]
print(x)