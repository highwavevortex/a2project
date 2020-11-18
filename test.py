import csv 

with open('MOCK_DATA.csv') as csvfile:    
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(dict(row))
