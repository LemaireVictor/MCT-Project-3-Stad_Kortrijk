import csv
from difflib import SequenceMatcher
import operator


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()  

testnaam = ["Stationstraat  " , "Knokstraat ", "Buda", "Amazones", "straat", "Bruyningaa"]

for naam in testnaam:
    f = open("straatnamen2.csv", "r")
    f.readline()
    names = f.readlines()
    NewName_percentage = {}
    naam_percentage = {}
    for name in names:
        name = name.split(",")
        name[1] = name[1].replace("\n", "")
        # check of de straatnaam een oude straatnaam is
        # vind hij similarities boven 75%
        # neem de naam met de hoogste similarity
        if similar(name[1].lower(),naam.lower()) >= 0.75:
            try:
                similarity = similar(name[1].lower(),naam.lower())
                NewName_percentage[name[0]] = similarity
                naam_percentage[naam] = similarity 
            except:
                pass
        # Vind hij geen similarities met oude straatnamen
        # kijk dan of hij bij de nieuwe straatnamen één vindt
        # neem de naam met de hoogste similarity
        elif similar(name[0].lower(),naam.lower()) >= 0.75:
            try:
                similarity = similar(name[0].lower(),naam.lower())
                NewName_percentage[name[0]] = similarity
                naam_percentage[naam] = similarity
            except:
                pass
        else:
            pass
    # print(NewName_percentage)
    # straatnaam niet in de csv file van kortrijk
    # zoek in 40 000 straatnamen van belgië
    # vind hij een similarity hoger dan 75%
    # schrijf de straatnaam vertaald door Het model
    # !!!!! schrijft niet de beste similarity naar de csv
    if naam not in naam_percentage and naam not in NewName_percentage:
        f = open("stratenNL.txt", "r")
        f.readline()
        names = f.readlines()
        for name in names:
            if similar(name[:-1].lower(),naam.lower()) >= 0.75:
                try:
                    similarity = similar(name[:-1].lower(),naam.lower())
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
        # make_csv(nieuwe_straatnaam, "straatnamen.csv", self.file_name)
    except:
        pass