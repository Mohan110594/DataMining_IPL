import boto3
import json
from time import sleep
import decimal

dynamo_db = boto3.resource('dynamodb')

table = dynamo_db.Table('Players')

with open('player_birth_info.json') as json_file:
    data = json.load(json_file,parse_float = decimal.Decimal)

count = 0
# print(type(data))

for key in data:
    if (count % 240 == 0):
        print(count, ' items done')
        sleep(10)
    # if (count > 149800):
    table.put_item(Item=data[key])
    count += 1