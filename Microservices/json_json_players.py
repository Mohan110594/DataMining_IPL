import json 
  
# Opening JSON file 
with open('player_birth_info_for_es_1.json') as json_file: 
    data = json.load(json_file) 

players_dict={}

for val in data:
    players_dict[val["uid"]]=val

json1 = json.dumps(players_dict)
f = open("players.json","w")
f.write(json1)
f.close()
