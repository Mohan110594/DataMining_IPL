import csv
import json
import datetime
import re
import pandas as pd
csvfile=r'C:\Users\nsnkr\Downloads\deliveries.csv'
newcsvfile=r'C:\Users\nsnkr\Downloads\deliveries1.csv'
jsonfile=r'C:\Users\nsnkr\Data_Mining_Project\deliveries.json'
deliveries = pd.read_csv(csvfile)
deliveries.fillna({'player_dismissed': 'Not Dismissed'}, inplace= True)
deliveries.fillna({'dismissal_kind': 'Not Dismissed'}, inplace= True)
deliveries.fillna({'fielder': 'Not Dismissed'}, inplace= True)
deliveries.to_csv(newcsvfile)
with open(newcsvfile) as csvfile1:
    reader_in=csv.DictReader(csvfile1)
    rows=[]
    for row in reader_in:
        rows.append(row)
with open(jsonfile,'w') as jsonfile1:
    jsonfile1.write(json.dumps(rows,indent=4))