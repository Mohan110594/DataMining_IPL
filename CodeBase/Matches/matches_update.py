import json
import boto3
import requests

# s3 = boto3.client('s3')
# response = s3.get_object(Bucket='bda-configurations', Key='es-config.json')
# response_2 = s3.get_object(Bucket='bda-configurations', Key='delivery_with_uid.json')
with open('es-config.json') as f:
  es_config = json.load(f)
# print(es_config)
with open('delivery_with_uid.json') as f:
  player_id_map = json.load(f)
# es_config = (json.loads(response['Body'].read()))
# player_id_map = (json.loads(response_2['Body'].read()))


def insert_into_es(each_doc, index, _id):
    try:
        insert_request = requests.post(url="{}/{}/_doc/{}".format(es_config['es_url'], index, _id),
                                       data=json.dumps(each_doc),
                                       headers=es_config['es_request_headers']).json()
        print(insert_request, 400)

    except Exception as es:
        exit(0)


def get_response(index, _id):
    # url = "http://3.138.201.253:9200/"+index + "/" + "_doc/" + _id
    match_info_response = requests.get(
        "{}/{}/_doc/{}".format(es_config['es_url'], index, _id)).json()
    # print(requests.get(url).json())
    # print(requests.get("http://3.138.201.253:9200/deliveries/_doc/L_2dH3YBzRl0tdQdmT78").json())
    return match_info_response


def update_player_info(player_id_map, pub_json, deliveries_info_response, player_type):
    try:
        if deliveries_info_response['found']:
            match_info = deliveries_info_response['_source']
            # print(match_info)
            #   Get ids of both batsman and bowler
            if player_type == 'batsman':
                player_id = player_id_map[match_info['batsman']]
            else:
                player_id = player_id_map[match_info['bowler']]
            print(player_id)

            #   Retrieve info of both bowler and batsman
            
            player_info = get_response(es_config['es_players_index'], player_id)
            print(player_info)
            player_info = player_info['_source']
            
            match_id = int(match_info['match_id'])

            #   Check whether matches dict is in _source
            if ('matches' not in player_info):
                player_info['matches'] = {}

            #   Check whether match id is in both players
            if (match_id not in player_info['matches']):
                player_info['matches'][match_id] = {}

            player_match_info = player_info['matches'][match_id]
            print("Players")
            # print(player_info)
            #   -------------------------------------------------------------------------------------------------------    #
            #   Initialize total runs, in parallel with balls faced if the player is a batsman

            if 'total_runs' not in player_match_info:
                player_match_info['total_runs'] = 0
            if 'balls_faced' not in player_match_info:
                player_match_info['balls_faced'] = 0

            if 'total_runs' not in player_info:
                player_info['total_runs'] = 0

                player_info['matches_30s'] = {}
                player_info['matches_50s'] = {}
                player_info['matches_100s'] = {}
                player_info['matches_150s'] = {}

                player_info['total_30s'] = 0
                player_info['total_50s'] = 0
                player_info['total_100s'] = 0
                player_info['total_150s'] = 0

            if 'balls_faced' not in player_info:
                player_info['balls_faced'] = 0
            # print(player_info)
            if (player_type == 'batsman'):
                #   Update total runs, in parallel with balls faced if the player is a batsman
                # print(type(match_info['total_runs']))
                # print(player_match_info)
                player_match_info['total_runs']+= int(match_info['total_runs'])
                player_match_info['balls_faced']+= 1
                # print(player_match_info)
                if player_match_info['total_runs'] >= 30:
                    player_info['matches_30s'][match_id] = True
                    player_info['total_30s'] = len(player_info['matches_30s'])
                if player_match_info['total_runs'] >= 50:
                    player_info['matches_50s'][match_id] = True
                    player_info['total_50s'] = len(player_info['matches_50s'])
                if player_match_info['total_runs'] >= 100:
                    player_info['matches_100s'][match_id] = True
                    player_info['total_100s'] = len(player_info['matches_100s'])
                if player_match_info['total_runs'] >= 150:
                    player_info['matches_150s'][match_id] = True
                    player_info['total_150s'] = len(player_info['matches_150s'])

                player_info['total_runs'] += int(match_info['total_runs'])
                player_info['balls_faced'] += 1
                # print(player_info)
            #   -------------------------------------------------------------------------------------------------------    #

            #   -------------------------------------------------------------------------------------------------------    #
            #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the entire match to zero
            if 'total_0s' not in player_match_info:
                player_match_info['total_0s'] = 0
            if 'total_1s' not in player_match_info:
                player_match_info['total_1s'] = 0
            if 'total_2s' not in player_match_info:
                player_match_info['total_2s'] = 0
            if 'total_3s' not in player_match_info:
                player_match_info['total_3s'] = 0
            if 'total_4s' not in player_match_info:
                player_match_info['total_4s'] = 0
            if 'total_5s' not in player_match_info:
                player_match_info['total_5s'] = 0
            if 'total_6s' not in player_match_info:
                player_match_info['total_6s'] = 0

            if 'total_0s' not in player_info:
                player_info['total_0s'] = 0
            if 'total_1s' not in player_info:
                player_info['total_1s'] = 0
            if 'total_2s' not in player_info:
                player_info['total_2s'] = 0
            if 'total_3s' not in player_info:
                player_info['total_3s'] = 0
            if 'total_4s' not in player_info:
                player_info['total_4s'] = 0
            if 'total_5s' not in player_info:
                player_info['total_5s'] = 0
            if 'total_6s' not in player_info:
                player_info['total_6s'] = 0
            # print(player_info)
            if player_type == 'batsman':
                # print(player_info)
                #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the match along with the corresponding batsman accordingly
                if int(match_info['total_runs']) == 0:
                    player_info['total_0s'] += 1
                    player_match_info['total_0s'] += 1
                if int(match_info['total_runs']) == 1:
                    player_info['total_1s'] += 1
                    player_match_info['total_1s'] += 1
                if int(match_info['total_runs']) == 2:
                    player_info['total_2s'] += 1
                    player_match_info['total_2s'] += 1
                if int(match_info['total_runs']) == 3:
                    player_info['total_3s'] += 1
                    player_match_info['total_3s'] += 1
                if int(match_info['total_runs']) == 4:
                    player_info['total_4s'] += 1
                    player_match_info['total_4s'] += 1
                if int(match_info['total_runs']) == 5:
                    player_info['total_5s'] += 1
                    player_match_info['total_5s'] += 1
                if int(match_info['total_runs']) >= 6:
                    player_info['total_6s'] += 1
                    player_match_info['total_6s'] += 1
                # print(player_info)
            #   -------------------------------------------------------------------------------------------------------    #

            #   -------------------------------------------------------------------------------------------------------    #
            #   Initialize total extras and total wickets for the entire match
            if 'total_runs_given' not in player_info:
                player_info['total_runs_given'] = 0

            if 'total_wickets' not in player_info:
                player_info['total_wickets'] = 0

                player_info['matches_3wh'] = {}
                player_info['matches_5wh'] = {}

                player_info['total_3wh'] = 0
                player_info['total_5wh'] = 0

            if 'balls_bowled' not in player_info:
                player_info['balls_bowled'] = 0

            if 'total_runs_given' not in player_match_info:
                player_match_info['total_runs_given'] = 0
            if 'total_wickets' not in player_match_info:
                player_match_info['total_wickets'] = 0
            if 'balls_bowled' not in player_match_info:
                player_match_info['balls_bowled'] = 0
            # print(player_match_info)
            if (player_type == 'bowler'):
                print(player_info)
                #   Update total extras and total wickets for the entire match
                if int(match_info['total_runs']) != 0:
                    player_info['total_runs_given'] += int(match_info['total_runs'])
                    player_match_info['total_runs_given'] += int(match_info['total_runs'])
                if match_info['dismissal_kind'] != 'Not Dismissed':
                    player_info['total_wickets'] += 1
                    player_match_info['total_wickets'] += 1

                    if player_match_info['total_wickets'] >= 3:
                        player_info['matches_3wh'][match_id] = True
                        player_info['total_3wh'] = len(player_info['matches_3wh'])

                    if player_match_info['total_wickets'] >= 5:
                        player_info['matches_5wh'][match_id] = True
                        player_info['total_5wh'] = len(player_info['matches_5wh'])

                player_info['balls_bowled'] += 1
                player_match_info['balls_bowled'] += 1
            #   -------------------------------------------------------------------------------------------------------    #
                # print(player_info)
            player_info['matches'][match_id] = player_match_info
            if player_type=='batsman':
                print(player_info)
            # print(player_info['matches'][match_id])
            return player_info, player_id

    except:
        print("Got here")
        # print(player_id_map, pub_json, deliveries_info_response, player_type)
        exit(0)
        # return {}, ''


event = {'Records': [{'eventID': '9f8e33e18130c92a1ece87041211a588', 'eventName': 'MODIFY', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-2', 'dynamodb': {'ApproximateCreationDateTime': 1606167468.0, 'Keys': {'id': {'S': "L_2dH3YBzRl0tdQdmT78"}}, 'NewImage': {'date': {'S': '05/18/2008'}, 'venue': {'S': 'Rajiv Gandhi International Stadium, Uppal'}, 'win_by_wickets': {'N': '0'}, 'city': {'S': 'Hyderabad'}, 'team1': {'S': 'Mumbai Indians'}, 'team2': {'S': 'Deccan Chargers'}, 'dl_applied': {'N': '0'}, 'result': {'S': 'normal'}, 'player_of_match': {'S': 'DJ Bravo'}, 'winner': {'S': 'Mumbai Indians'}, 'umpire1': {'S': 'BR Doctrove'}, 'season': {'N': '2008'}, 'toss_winner': {'S': 'Deccan Chargers'}, 'umpire3': {'S': ''}, 'id': {'S': "L_2dH3YBzRl0tdQdmT78"}, 'umpire2': {'S': 'DJ Harper'}, 'toss_decision': {'S': 'field'}, 'win_by_runs': {'N': '35'}}, 'OldImage': {'date': {'S': '05/18/2008'}, 'venue': {'S': 'Rajiv Gandhi International Stadium, Uppal'}, 'win_by_wickets': {'N': '0'}, 'city': {'S': 'Hyderabad'}, 'team1': {'S': 'Mumbai Indians'}, 'team2': {'S': 'Deccan Chargers'}, 'dl_applied': {'N': '0'}, 'result': {'S': 'normal'}, 'player_of_match': {'S': 'DJ Bravo'}, 'winner': {'S': 'Mumbai Indians'}, 'umpire1': {'S': 'BR Doctrove'}, 'season': {'N': '2008'}, 'toss_winner': {'S': 'Deccan Chargers'}, 'umpire3': {'S': ''}, 'id': {'S': "L_2dH3YBzRl0tdQdmT78"}, 'umpire2': {'S': 'DJ Harper'}, 'toss_decision': {'S': 'field'}, 'win_by_runs': {'N': '25'}}, 'SequenceNumber': '89234200000000002923934217', 'SizeBytes': 615, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'eventSourceARN': 'arn:aws:dynamodb:us-east-2:615533125910:table/Matches/stream/2020-11-23T20:55:49.105'}]}
def update_match_info(pub_json, match_info_response):
    if match_info_response['found']:
        match_info = match_info_response['_source']
        # print("Pub")
        # print(pub_json['date'])
        print(match_info)

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total runs (innings 1 and 2 separately), in parallel with balls faced if the player is a batsman
        if 'total_runs_inn1' not in match_info:
            match_info['total_runs_inn1'] = 0
        if 'total_runs_inn2' not in match_info:
            match_info['total_runs_inn2'] = 0
        if 'total_runs' not in match_info:
            match_info['total_runs'] = 0

        #   Update total runs (innings 1 and 2 separately), in parallel with balls faced if the player is a batsman
        if match_info['inning'] == 1:#Initially pub_json
            match_info['total_runs_inn1'] += match_info['total_runs']
        if match_info['inning'] == 2:
            match_info['total_runs_inn2'] += match_info['total_runs']
        match_info['total_runs'] += match_info['total_runs']
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the entire match to zero
        if 'total_0s' not in match_info:
            match_info['total_0s'] = 0
        if 'total_1s' not in match_info:
            match_info['total_1s'] = 0
        if 'total_2s' not in match_info:
            match_info['total_2s'] = 0
        if 'total_3s' not in match_info:
            match_info['total_3s'] = 0
        if 'total_4s' not in match_info:
            match_info['total_4s'] = 0
        if 'total_5s' not in match_info:
            match_info['total_5s'] = 0
        if 'total_6s' not in match_info:
            match_info['total_6s'] = 0

        #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the match along with the corresponding batsman accordingly
        if match_info['total_runs'] == '0':
            match_info['total_0s'] += 1

        if match_info['total_runs'] == '1':
            match_info['total_1s'] += 1

        if match_info['total_runs'] == '2':
            match_info['total_2s'] += 1

        if match_info['total_runs'] == '3':
            match_info['total_3s'] += 1

        if match_info['total_runs'] == '4':
            match_info['total_4s'] += 1

        if match_info['total_runs'] == '5':
            match_info['total_5s'] += 1

        if int(match_info['total_runs']) >= 6:
            match_info['total_6s'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the first innings to zero
        if 'total_0s_inn1' not in match_info:
            match_info['total_0s_inn1'] = 0
        if 'total_1s_inn1' not in match_info:
            match_info['total_1s_inn1'] = 0
        if 'total_2s_inn1' not in match_info:
            match_info['total_2s_inn1'] = 0
        if 'total_3s_inn1' not in match_info:
            match_info['total_3s_inn1'] = 0
        if 'total_4s_inn1' not in match_info:
            match_info['total_4s_inn1'] = 0
        if 'total_5s_inn1' not in match_info:
            match_info['total_5s_inn1'] = 0
        if 'total_6s_inn1' not in match_info:
            match_info['total_6s_inn1'] = 0

        #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the first innings accordingly
        if match_info['total_runs'] == 0 and match_info['inning'] == 1:
            match_info['total_0s_inn1'] += 1
        if int(match_info['total_runs']) == 1 and int(match_info['inning']) == 1:
            match_info['total_1s_inn1'] += 1
        if match_info['total_runs'] == 2 and match_info['inning'] == 1:
            match_info['total_2s_inn1'] += 1
        if match_info['total_runs'] == 3 and match_info['inning'] == 1:
            match_info['total_3s_inn1'] += 1
        if match_info['total_runs'] == 4 and match_info['inning'] == 1:
            match_info['total_4s_inn1'] += 1
        if match_info['total_runs'] == 5 and match_info['inning'] == 1:
            match_info['total_5s_inn1'] += 1
        if int(match_info['total_runs']) >= 6 and match_info['inning'] == 1:
            match_info['total_6s_inn1'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the second innings to zero
        if 'total_0s_inn2' not in match_info:
            match_info['total_0s_inn2'] = 0
        if 'total_1s_inn2' not in match_info:
            match_info['total_1s_inn2'] = 0
        if 'total_2s_inn2' not in match_info:
            match_info['total_2s_inn2'] = 0
        if 'total_3s_inn2' not in match_info:
            match_info['total_3s_inn2'] = 0
        if 'total_4s_inn2' not in match_info:
            match_info['total_4s_inn2'] = 0
        if 'total_5s_inn2' not in match_info:
            match_info['total_5s_inn2'] = 0
        if 'total_6s_inn2' not in match_info:
            match_info['total_6s_inn2'] = 0

        if 'total_extras' not in match_info:
            match_info['total_extras'] = 0

        #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the second innings accordingly
        if match_info['total_runs'] == 0 and match_info['inning'] == 2:
            match_info['total_0s_inn2'] += 1
        if int(match_info['total_runs']) == 1 and int(match_info['inning']) == 2:
            match_info['total_1s_inn2'] += 1
        if match_info['total_runs'] == 2 and match_info['inning'] == 2:
            match_info['total_2s_inn2'] += 1
        if match_info['total_runs'] == 3 and match_info['inning'] == 2:
            match_info['total_3s_inn2'] += 1
        if match_info['total_runs'] == 4 and match_info['inning'] == 2:
            match_info['total_4s_inn2'] += 1
        if match_info['total_runs'] == 5 and match_info['inning'] == 2:
            match_info['total_5s_inn2'] += 1
        if int(match_info['total_runs']) >= 6 and int(match_info['inning']) == 2:
            match_info['total_6s_inn2'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Update total extras and total wickets for the entire match
        if match_info['extra_runs'] != 0:
            match_info['total_extras'] += int(match_info['extra_runs'])

        if match_info['dismissal_kind'] != 'Not Dismissed':
            match_info['total_wickets'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total extras and total wickets for the first innings
        if 'total_extras_inn1' not in match_info:
            match_info['total_extras_inn1'] = 0
        if 'total_wickets_inn1' not in match_info:
            match_info['total_wickets_inn1'] = 0

        #   Update total extras and total wickets for the first innings
        if match_info['extra_runs'] != 0 and match_info['inning'] == 1:
            match_info['total_extras_inn1'] += match_info['extra_runs']
        if match_info['dismissal_kind'] != 'Not Dismissed' and match_info['inning'] == 1:
            match_info['total_wickets_inn1'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total extras and total wickets for the second innings
        if 'total_extras_inn2' not in match_info:
            match_info['total_extras_inn2'] = 0
        if 'total_wickets_inn2' not in match_info:
            match_info['total_wickets_inn2'] = 0

        #   Update total extras and total wickets for the second innings
        if match_info['extra_runs'] != 0 and match_info['inning'] == 2:
            match_info['total_extras_inn2'] += match_info['extra_runs']
        if match_info['dismissal_kind'] != 'Not Dismissed' and match_info['inning'] == 2:
            match_info['total_wickets_inn2'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        return match_info

    return {}


def lambda_handler(event):
    # TODO implement

    for each_ in event['Records']:
        action = each_['eventName']

        if (action == 'INSERT' or action == 'MODIFY'):

            currentEvent = each_['dynamodb']['NewImage']
            for key, valueDict in currentEvent.items():
                for dataType, finalValue in valueDict.items():
                    if dataType == 'N':
                        currentEvent[key] = float(finalValue)
                    elif dataType == 'S':
                        currentEvent[key] = str(finalValue)

            deliveries_info_response = get_response(es_config['es_deliveries_index'], "L_2dH3YBzRl0tdQdmT78")
            print(deliveries_info_response)
            # print(currentEvent)
            match_info = update_match_info(currentEvent, deliveries_info_response)
            print(match_info)
            # print("Hello")
            player_info_1, pid_1 = update_player_info(player_id_map, currentEvent, deliveries_info_response, 'batsman')
            # player_info_2, pid_2 = update_player_info(player_id_map, currentEvent, deliveries_info_response, 'bowler')

            # insert_into_es(currentEvent, es_config['es_deliveries_index'], currentEvent['id'])

            # insert_into_es(match_info, es_config['es_matches_index'], int(match_info['match_id']))
            print(match_info['match_id'])
            # insert_into_es(player_info_1, es_config['es_players_index'], pid_1)
            # insert_into_es(player_info_2, es_config['es_players_index'], pid_2)

    # response = requests.post('http://34.227.172.158:3718/', json=json.dumps(currentEvent))

lambda_handler(event)





#     import json
# import boto3
# from botocore.vendored import requests

# s3 = boto3.client('s3')
# response = s3.get_object(Bucket='dmipldata', Key='es-config.json')
# response_2 = s3.get_object(Bucket='dmipldata', Key='delivery_with_uid.json')

# es_config = (json.loads(response['Body'].read()))
# player_id_map = (json.loads(response_2['Body'].read()))


# def insert_into_es(each_doc, index, _id):
#     try:
#         insert_request = requests.post(url="{}/{}/_doc/{}".format(es_config['es_url'], index, _id),
#                                        data=json.dumps(each_doc),
#                                        headers=es_config['es_request_headers']).json()
#         print(insert_request, 400)

#     except Exception as es:
#         exit(0)


# def get_response(index, _id):
#     match_info_response = requests.get(
#         "{}/{}/_doc/{}".format(es_config['es_url'], index, _id)).json()

#     return match_info_response


# def update_player_info(player_id_map, pub_json, deliveries_info_response, player_type):
#     try:
#         if deliveries_info_response['found']:
#             match_info = deliveries_info_response['_source']

#             #   Get ids of both batsman and bowler
#             if player_type == 'batsman':
#                 player_id = player_id_map[pub_json['batsman']]
#             else:
#                 player_id = player_id_map[pub_json['bowler']]

#             #   Retrieve info of both bowler and batsman
#             player_info = get_response(es_config['es_players_index'], player_id)
#             player_info = player_info['_source']

#             match_id = int(match_info['match_id'])

#             #   Check whether matches dict is in _source
#             if ('matches' not in player_info):
#                 player_info['matches'] = {}

#             #   Check whether match id is in both players
#             if (match_id not in player_info['matches']):
#                 player_info['matches'][match_id] = {}

#             player_match_info = player_info['matches'][match_id]

#             #   -------------------------------------------------------------------------------------------------------    #
#             #   Initialize total runs, in parallel with balls faced if the player is a batsman

#             if 'total_runs' not in player_match_info:
#                 player_match_info['total_runs'] = 0
#             if 'balls_faced' not in player_match_info:
#                 player_match_info['balls_faced'] = 0

#             if 'total_runs' not in player_info:
#                 player_info['total_runs'] = 0

#                 player_info['matches_30s'] = {}
#                 player_info['matches_50s'] = {}
#                 player_info['matches_100s'] = {}
#                 player_info['matches_150s'] = {}

#                 player_info['total_30s'] = 0
#                 player_info['total_50s'] = 0
#                 player_info['total_100s'] = 0
#                 player_info['total_150s'] = 0

#             if 'balls_faced' not in player_info:
#                 player_info['balls_faced'] = 0

#             if (player_type == 'batsman'):
#                 #   Update total runs, in parallel with balls faced if the player is a batsman
#                 player_match_info['total_runs'] += pub_json['total_runs']
#                 player_match_info['balls_faced'] += 1

#                 if player_match_info['total_runs'] >= 30:
#                     player_info['matches_30s'][match_id] = True
#                     player_info['total_30s'] = len(player_info['matches_30s'])
#                 if player_match_info['total_runs'] >= 50:
#                     player_info['matches_50s'][match_id] = True
#                     player_info['total_50s'] = len(player_info['matches_50s'])
#                 if player_match_info['total_runs'] >= 100:
#                     player_info['matches_100s'][match_id] = True
#                     player_info['total_100s'] = len(player_info['matches_100s'])
#                 if player_match_info['total_runs'] >= 150:
#                     player_info['matches_150s'][match_id] = True
#                     player_info['total_150s'] = len(player_info['matches_150s'])

#                 player_info['total_runs'] += pub_json['total_runs']
#                 player_info['balls_faced'] += 1
#             #   -------------------------------------------------------------------------------------------------------    #

#             #   -------------------------------------------------------------------------------------------------------    #
#             #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the entire match to zero
#             if 'total_0s' not in player_match_info:
#                 player_match_info['total_0s'] = 0
#             if 'total_1s' not in player_match_info:
#                 player_match_info['total_1s'] = 0
#             if 'total_2s' not in player_match_info:
#                 player_match_info['total_2s'] = 0
#             if 'total_3s' not in player_match_info:
#                 player_match_info['total_3s'] = 0
#             if 'total_4s' not in player_match_info:
#                 player_match_info['total_4s'] = 0
#             if 'total_5s' not in player_match_info:
#                 player_match_info['total_5s'] = 0
#             if 'total_6s' not in player_match_info:
#                 player_match_info['total_6s'] = 0

#             if 'total_0s' not in player_info:
#                 player_info['total_0s'] = 0
#             if 'total_1s' not in player_info:
#                 player_info['total_1s'] = 0
#             if 'total_2s' not in player_info:
#                 player_info['total_2s'] = 0
#             if 'total_3s' not in player_info:
#                 player_info['total_3s'] = 0
#             if 'total_4s' not in player_info:
#                 player_info['total_4s'] = 0
#             if 'total_5s' not in player_info:
#                 player_info['total_5s'] = 0
#             if 'total_6s' not in player_info:
#                 player_info['total_6s'] = 0

#             if player_type == 'batsman':

#                 #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the match along with the corresponding batsman accordingly
#                 if pub_json['total_runs'] == 0:
#                     player_info['total_0s'] += 1
#                     player_match_info['total_0s'] += 1
#                 if pub_json['total_runs'] == 1:
#                     player_info['total_1s'] += 1
#                     player_match_info['total_1s'] += 1
#                 if pub_json['total_runs'] == 2:
#                     player_info['total_2s'] += 1
#                     player_match_info['total_2s'] += 1
#                 if pub_json['total_runs'] == 3:
#                     player_info['total_3s'] += 1
#                     player_match_info['total_3s'] += 1
#                 if pub_json['total_runs'] == 4:
#                     player_info['total_4s'] += 1
#                     player_match_info['total_4s'] += 1
#                 if pub_json['total_runs'] == 5:
#                     player_info['total_5s'] += 1
#                     player_match_info['total_5s'] += 1
#                 if pub_json['total_runs'] >= 6:
#                     player_info['total_6s'] += 1
#                     player_match_info['total_6s'] += 1
#             #   -------------------------------------------------------------------------------------------------------    #

#             #   -------------------------------------------------------------------------------------------------------    #
#             #   Initialize total extras and total wickets for the entire match
#             if 'total_runs_given' not in player_info:
#                 player_info['total_runs_given'] = 0

#             if 'total_wickets' not in player_info:
#                 player_info['total_wickets'] = 0

#                 player_info['matches_3wh'] = {}
#                 player_info['matches_5wh'] = {}

#                 player_info['total_3wh'] = 0
#                 player_info['total_5wh'] = 0

#             if 'balls_bowled' not in player_info:
#                 player_info['balls_bowled'] = 0

#             if 'total_runs_given' not in player_match_info:
#                 player_match_info['total_runs_given'] = 0
#             if 'total_wickets' not in player_match_info:
#                 player_match_info['total_wickets'] = 0
#             if 'balls_bowled' not in player_match_info:
#                 player_match_info['balls_bowled'] = 0

#             if (player_type == 'bowler'):

#                 #   Update total extras and total wickets for the entire match
#                 if pub_json['total_runs'] != 0:
#                     player_info['total_runs_given'] += pub_json['total_runs']
#                     player_match_info['total_runs_given'] += pub_json['total_runs']
#                 if pub_json['dismissal_kind'] != 'Not Dismissed':
#                     player_info['total_wickets'] += 1
#                     player_match_info['total_wickets'] += 1

#                     if player_match_info['total_wickets'] >= 3:
#                         player_info['matches_3wh'][match_id] = True
#                         player_info['total_3wh'] = len(player_info['matches_3wh'])

#                     if player_match_info['total_wickets'] >= 5:
#                         player_info['matches_5wh'][match_id] = True
#                         player_info['total_5wh'] = len(player_info['matches_5wh'])

#                 player_info['balls_bowled'] += 1
#                 player_match_info['balls_bowled'] += 1
#             #   -------------------------------------------------------------------------------------------------------    #

#             player_info['matches'][match_id] = player_match_info

#             return player_info, player_id

#     except:
#         print(player_id_map, pub_json, deliveries_info_response, player_type)
#         exit(0)
#         # return {}, ''


# def update_match_info(pub_json, match_info_response):
#     if match_info_response['found']:
#         match_info = match_info_response['_source']

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Initialize total runs (innings 1 and 2 separately), in parallel with balls faced if the player is a batsman
#         if 'total_runs_inn1' not in match_info:
#             match_info['total_runs_inn1'] = 0
#         if 'total_runs_inn2' not in match_info:
#             match_info['total_runs_inn2'] = 0
#         if 'total_runs' not in match_info:
#             match_info['total_runs'] = 0

#         #   Update total runs (innings 1 and 2 separately), in parallel with balls faced if the player is a batsman
#         if pub_json['inning'] == 1:
#             match_info['total_runs_inn1'] += pub_json['total_runs']
#         if pub_json['inning'] == 2:
#             match_info['total_runs_inn2'] += pub_json['total_runs']
#         match_info['total_runs'] += pub_json['total_runs']
#         #   -------------------------------------------------------------------------------------------------------    #

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the entire match to zero
#         if 'total_0s' not in match_info:
#             match_info['total_0s'] = 0
#         if 'total_1s' not in match_info:
#             match_info['total_1s'] = 0
#         if 'total_2s' not in match_info:
#             match_info['total_2s'] = 0
#         if 'total_3s' not in match_info:
#             match_info['total_3s'] = 0
#         if 'total_4s' not in match_info:
#             match_info['total_4s'] = 0
#         if 'total_5s' not in match_info:
#             match_info['total_5s'] = 0
#         if 'total_6s' not in match_info:
#             match_info['total_6s'] = 0

#         #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the match along with the corresponding batsman accordingly
#         if pub_json['total_runs'] == 0:
#             match_info['total_0s'] += 1

#         if pub_json['total_runs'] == 1:
#             match_info['total_1s'] += 1

#         if pub_json['total_runs'] == 2:
#             match_info['total_2s'] += 1

#         if pub_json['total_runs'] == 3:
#             match_info['total_3s'] += 1

#         if pub_json['total_runs'] == 4:
#             match_info['total_4s'] += 1

#         if pub_json['total_runs'] == 5:
#             match_info['total_5s'] += 1

#         if pub_json['total_runs'] >= 6:
#             match_info['total_6s'] += 1
#         #   -------------------------------------------------------------------------------------------------------    #

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the first innings to zero
#         if 'total_0s_inn1' not in match_info:
#             match_info['total_0s_inn1'] = 0
#         if 'total_1s_inn1' not in match_info:
#             match_info['total_1s_inn1'] = 0
#         if 'total_2s_inn1' not in match_info:
#             match_info['total_2s_inn1'] = 0
#         if 'total_3s_inn1' not in match_info:
#             match_info['total_3s_inn1'] = 0
#         if 'total_4s_inn1' not in match_info:
#             match_info['total_4s_inn1'] = 0
#         if 'total_5s_inn1' not in match_info:
#             match_info['total_5s_inn1'] = 0
#         if 'total_6s_inn1' not in match_info:
#             match_info['total_6s_inn1'] = 0

#         #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the first innings accordingly
#         if pub_json['total_runs'] == 0 and pub_json['inning'] == 1:
#             match_info['total_0s_inn1'] += 1
#         if pub_json['total_runs'] == 1 and pub_json['inning'] == 1:
#             match_info['total_1s_inn1'] += 1
#         if pub_json['total_runs'] == 2 and pub_json['inning'] == 1:
#             match_info['total_2s_inn1'] += 1
#         if pub_json['total_runs'] == 3 and pub_json['inning'] == 1:
#             match_info['total_3s_inn1'] += 1
#         if pub_json['total_runs'] == 4 and pub_json['inning'] == 1:
#             match_info['total_4s_inn1'] += 1
#         if pub_json['total_runs'] == 5 and pub_json['inning'] == 1:
#             match_info['total_5s_inn1'] += 1
#         if pub_json['total_runs'] >= 6 and pub_json['inning'] == 1:
#             match_info['total_6s_inn1'] += 1
#         #   -------------------------------------------------------------------------------------------------------    #

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Initilalize total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the second innings to zero
#         if 'total_0s_inn2' not in match_info:
#             match_info['total_0s_inn2'] = 0
#         if 'total_1s_inn2' not in match_info:
#             match_info['total_1s_inn2'] = 0
#         if 'total_2s_inn2' not in match_info:
#             match_info['total_2s_inn2'] = 0
#         if 'total_3s_inn2' not in match_info:
#             match_info['total_3s_inn2'] = 0
#         if 'total_4s_inn2' not in match_info:
#             match_info['total_4s_inn2'] = 0
#         if 'total_5s_inn2' not in match_info:
#             match_info['total_5s_inn2'] = 0
#         if 'total_6s_inn2' not in match_info:
#             match_info['total_6s_inn2'] = 0

#         #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the second innings accordingly
#         if pub_json['total_runs'] == 0 and pub_json['inning'] == 2:
#             match_info['total_0s_inn2'] += 1
#         if pub_json['total_runs'] == 1 and pub_json['inning'] == 2:
#             match_info['total_1s_inn2'] += 1
#         if pub_json['total_runs'] == 2 and pub_json['inning'] == 2:
#             match_info['total_2s_inn2'] += 1
#         if pub_json['total_runs'] == 3 and pub_json['inning'] == 2:
#             match_info['total_3s_inn2'] += 1
#         if pub_json['total_runs'] == 4 and pub_json['inning'] == 2:
#             match_info['total_4s_inn2'] += 1
#         if pub_json['total_runs'] == 5 and pub_json['inning'] == 2:
#             match_info['total_5s_inn2'] += 1
#         if pub_json['total_runs'] >= 6 and pub_json['inning'] == 2:
#             match_info['total_6s_inn2'] += 1
#         #   -------------------------------------------------------------------------------------------------------    #

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Update total extras and total wickets for the entire match
#         if pub_json['extra_runs'] != 0:
#             match_info['total_extras'] += pub_json['extra_runs']

#         if pub_json['dismissal_kind'] != 'Not Dismissed':
#             match_info['total_wickets'] += 1
#         #   -------------------------------------------------------------------------------------------------------    #

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Initialize total extras and total wickets for the first innings
#         if 'total_extras_inn1' not in match_info:
#             match_info['total_extras_inn1'] = 0
#         if 'total_wickets_inn1' not in match_info:
#             match_info['total_wickets_inn1'] = 0

#         #   Update total extras and total wickets for the first innings
#         if pub_json['extra_runs'] != 0 and pub_json['inning'] == 1:
#             match_info['total_extras_inn1'] += pub_json['extra_runs']
#         if pub_json['dismissal_kind'] != 'Not Dismissed' and pub_json['inning'] == 1:
#             match_info['total_wickets_inn1'] += 1
#         #   -------------------------------------------------------------------------------------------------------    #

#         #   -------------------------------------------------------------------------------------------------------    #
#         #   Initialize total extras and total wickets for the second innings
#         if 'total_extras_inn2' not in match_info:
#             match_info['total_extras_inn2'] = 0
#         if 'total_wickets_inn2' not in match_info:
#             match_info['total_wickets_inn2'] = 0

#         #   Update total extras and total wickets for the second innings
#         if pub_json['extra_runs'] != 0 and pub_json['inning'] == 2:
#             match_info['total_extras_inn2'] += pub_json['extra_runs']
#         if pub_json['dismissal_kind'] != 'Not Dismissed' and pub_json['inning'] == 2:
#             match_info['total_wickets_inn2'] += 1
#         #   -------------------------------------------------------------------------------------------------------    #

#         return match_info

#     return {}


# def lambda_handler(event, context):
#     # TODO implement

#     for each_ in event['Records']:
#         action = each_['eventName']

#         if (action == 'INSERT' or action == 'MODIFY'):

#             currentEvent = each_['dynamodb']['NewImage']
#             for key, valueDict in currentEvent.items():
#                 for dataType, finalValue in valueDict.items():
#                     if dataType == 'N':
#                         currentEvent[key] = float(finalValue)
#                     elif dataType == 'S':
#                         currentEvent[key] = str(finalValue)

#             deliveries_info_response = get_response(es_config['es_deliveries_index'], currentEvent['id'])

#             match_info = update_match_info(currentEvent, deliveries_info_response)

#             player_info_1, pid_1 = update_player_info(player_id_map, currentEvent, deliveries_info_response, 'batsman')
#             player_info_2, pid_2 = update_player_info(player_id_map, currentEvent, deliveries_info_response, 'bowler')

#             insert_into_es(currentEvent, es_config['es_deliveries_index'], currentEvent['id'])

#             insert_into_es(match_info, es_config['es_matches_index'], int(match_info['match_id']))

#             insert_into_es(player_info_1, es_config['es_players_index'], pid_1)
#             insert_into_es(player_info_2, es_config['es_players_index'], pid_2)