import csv 
import json 
  
  
# Function to convert a CSV to JSON 
# Takes the file paths as arguments 
def make_json(csvFilePath, jsonFilePath): 
      
    # create a dictionary 
    data = {} 
      
    # Open a csv reader called DictReader 
    with open(csvFilePath, encoding='utf-8') as csvf: 
        csvReader = csv.DictReader(csvf) 
          
        # Convert each row into a dictionary  
        # and add it to data 
        for rows in csvReader: 
              
            # Assuming a column named 'No' to 
            # be the primary key 
            key = rows["id"]
            rows["season"]=int(rows["season"])
            rows["dl_applied"]=int(rows["dl_applied"])
            rows["win_by_runs"]=int(rows["win_by_runs"])
            rows["win_by_wickets"]=int(rows["win_by_wickets"])
            loc={"lat":float(rows["latitude"]),"lon":float(rows["longitude"])}
            rows["location"]=loc
            del rows["latitude"]
            del rows["longitude"]
            data[key] = rows 
            
  
    # Open a json writer, and use the json.dumps()  
    # function to dump data 
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonf.write(json.dumps(data, indent=4)) 
          
# Driver Code 
  
# Decide the two file paths according to your  
# computer system 
csvFilePath = r'matches_latlong.csv'
jsonFilePath = r'final_matches.json'
  
# Call the make_json function 
make_json(csvFilePath, jsonFilePath)