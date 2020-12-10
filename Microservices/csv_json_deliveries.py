import csv 
import json 
  
  
# Function to convert a CSV to JSON 
# Takes the file paths as arguments 
def make_json(csvFilePath, jsonFilePath,out): 
      
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
            key = int(rows["no"])
            
            rows["inning"]=int(rows["inning"])
            rows["over"]=int(rows["over"])
            rows["ball"]=int(rows["ball"])
            rows["is_super_over"]=int(rows["is_super_over"])
            rows["wide_runs"]=int(rows["wide_runs"])
            rows["legbye_runs"]=int(rows["legbye_runs"])
            rows["noball_runs"]=int(rows["noball_runs"])
            rows["penalty_runs"]=int(rows["penalty_runs"])
            rows["batsman_runs"]=int(rows["batsman_runs"])
            rows["extra_runs"]=int(rows["extra_runs"])
            rows["total_runs"]=int(rows["total_runs"])
            # rows["match_id"]=int(rows["match_id"])
            rows["bye_runs"]=int(rows["bye_runs"])
            out.append(rows)
            data[key] = rows 
  
    # Open a json writer, and use the json.dumps()  
    # function to dump data 
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf: 
        jsonf.write(json.dumps(data, indent=4)) 

    with open(jsonFilePath_new, 'w', encoding='utf-8') as jsonf: 
        jsonf.write(json.dumps(out)) 
          
# Driver Code 
  
# Decide the two file paths according to your  
# computer system 
csvFilePath = r'deliveries.csv'
jsonFilePath = r'final_deliveries.json'
jsonFilePath_new = r'final_out_deliveries.json'
  
# Call the make_json function 
out=[]
make_json(csvFilePath, jsonFilePath,out)