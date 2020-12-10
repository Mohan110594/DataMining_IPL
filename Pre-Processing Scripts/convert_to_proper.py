import boto3
import json
from time import sleep
import decimal

with open('players_finalsome.json') as json_file:
    data = json.load(json_file,parse_float = decimal.Decimal)
list_of_dict = []
for key,val in data.items():
    # print(key,val)
    sample_dict = {}
    sample_dict[key] = val
    # list_of_dict.append(sample_dict)
    list_of_dict.append(val)

# print(list_of_dict)
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

with open('players_final.json','w') as json_file:
    json.dump(list_of_dict,json_file,default = decimal_default)