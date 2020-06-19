from difflib import SequenceMatcher
import csv
naam = "straat"

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

f = open("straten.txt", "r")
f.readline()
names = f.readlines()

for name in names:
    if similar(name[:-1].lower(),naam.lower()) > 0.7:
        sim = similar(name[:-1].lower(),naam.lower())
        print("gevonden: " + name[:-1] + " ---- " + naam + " ---- " + str(sim))




# with open('straatnamen.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print(row['straatnaam'])



