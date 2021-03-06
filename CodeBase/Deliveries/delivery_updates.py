import json
import boto3
import requests
#
# s3 = boto3.client('s3')
# response = s3.get_object(Bucket='bda-configurations', Key='es-config.json')
# response_2 = s3.get_object(Bucket='bda-configurations', Key='delivery_with_uid.json')
#
# es_config = (json.loads(response['Body'].read()))
with open('es-config.json') as f:
  es_config = json.load(f)
# print(es_config)
with open('delivery_with_uid.json') as f:
  player_id_map = json.load(f)
# player_id_map = (json.loads(response_2['Body'].read()))


def insert_into_es(each_doc, index, _id):
    try:
        insert_request = requests.post(url="{}/{}/_doc/{}".format(es_config['es_url'], index, _id),
                                       data=json.dumps(each_doc),
                                       headers=es_config['es_request_headers']).json()
        # print(each_doc,index,insert_request)
        # print(each_doc, index, _id)

    except Exception as es:
        print(each_doc, index, _id,"exception",insert_request)
        print(str(es))
        exit(0)


def get_response(index, _id):
    match_info_response = requests.get(
        "{}/{}/_doc/{}".format(es_config['es_url'], index, _id)).json()

    return match_info_response


def update_player_info(player_id_map, pub_json, player_info_response, player_type):
    try:
        if player_info_response['found']:
            # match_info = deliveries_info_response['_source']

            #   Get ids of both batsman and bowler
            # if player_type == 'batsman':
            #     player_id = player_id_map[pub_json['batsman']]
            # else:
            #     player_id = player_id_map[pub_json['bowler']]
            player_id = player_info_response['_id']
            #   Retrieve info of both bowler and batsman
            # player_info = get_response(es_config['es_players_index'], player_id)
            player_info = player_info_response['_source']
            # print(player_info, 'before')
            match_id = str(pub_json['match_id'])

            #   Check whether matches dict is in _source
            if 'matches' not in player_info:
                player_info['matches'] = {}
                player_info['total_matches_played'] = 0

            #   Check whether match id is in both players
            # print(type(match_id))
            if match_id not in player_info['matches']:
                player_info['matches'] = {}
                player_info['matches'][match_id] = {}
                player_info['total_matches_played'] += 1

            player_match_info = player_info['matches'][match_id]

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

            if (player_type == 'batsman'):
                #   Update total runs, in parallel with balls faced if the player is a batsman
                player_match_info['total_runs'] += pub_json['total_runs']
                player_match_info['balls_faced'] += 1

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

                player_info['total_runs'] += pub_json['total_runs']
                player_info['balls_faced'] += 1
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

            if player_type == 'batsman':

                #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the match along with the corresponding batsman accordingly
                if pub_json['total_runs'] == 0:
                    player_info['total_0s'] += 1
                    player_match_info['total_0s'] += 1
                if pub_json['total_runs'] == 1:
                    player_info['total_1s'] += 1
                    player_match_info['total_1s'] += 1
                if pub_json['total_runs'] == 2:
                    player_info['total_2s'] += 1
                    player_match_info['total_2s'] += 1
                if pub_json['total_runs'] == 3:
                    player_info['total_3s'] += 1
                    player_match_info['total_3s'] += 1
                if pub_json['total_runs'] == 4:
                    player_info['total_4s'] += 1
                    player_match_info['total_4s'] += 1
                if pub_json['total_runs'] == 5:
                    player_info['total_5s'] += 1
                    player_match_info['total_5s'] += 1
                if pub_json['total_runs'] >= 6:
                    player_info['total_6s'] += 1
                    player_match_info['total_6s'] += 1
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

            if (player_type == 'bowler'):

                #   Update total extras and total wickets for the entire match
                if pub_json['total_runs'] != 0:
                    player_info['total_runs_given'] += pub_json['total_runs']
                    player_match_info['total_runs_given'] += pub_json['total_runs']
                if pub_json['dismissal_kind'] != 'Not Dismissed':
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

            player_info['matches'][match_id] = player_match_info
            # print(player_info, 'updated')
            return player_info, player_id

    except:
        print(player_id_map, pub_json, player_info_response, player_type)
        exit(0)
        # return {}, ''


def update_match_info(pub_json, match_info_response):
    if match_info_response['found']:
        match_info = match_info_response['_source']
        # print("before", match_info)

        # Initialize batsman and bowler dictionaries to setup a player's combined profile
        # if pub_json['batsman'] not in match_info:
        #     match_info[pub_json['batsman']] = {}
        # if pub_json['bowler'] not in match_info:
        #     match_info[pub_json['bowler']] = {}

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total runs (innings 1 and 2 separately), in parallel with balls faced if the player is a batsman
        if 'total_runs_inn1' not in match_info:
            match_info['total_runs_inn1'] = 0
        if 'total_runs_inn2' not in match_info:
            match_info['total_runs_inn2'] = 0
        if 'total_runs' not in match_info:
            match_info['total_runs'] = 0
        # if 'total_runs' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_runs'] = 0
        # if 'balls_faced' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['balls_faced'] = 0

        #   Update total runs (innings 1 and 2 separately), in parallel with balls faced if the player is a batsman
        if pub_json['inning'] == 1:
            match_info['total_runs_inn1'] += pub_json['total_runs']
        if pub_json['inning'] == 2:
            match_info['total_runs_inn2'] += pub_json['total_runs']
        match_info['total_runs'] += pub_json['total_runs']
        # match_info[pub_json['batsman']]['total_runs'] += pub_json['total_runs']
        # match_info[pub_json['batsman']]['balls_faced'] += 1
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

        #   Initialize total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the batsman for the entire match to zero
        # if 'total_0s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_0s'] = 0
        # if 'total_1s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_1s'] = 0
        # if 'total_2s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_2s'] = 0
        # if 'total_3s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_3s'] = 0
        # if 'total_4s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_4s'] = 0
        # if 'total_5s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_5s'] = 0
        # if 'total_6s' not in match_info[pub_json['batsman']]:
        #     match_info[pub_json['batsman']]['total_6s'] = 0

        #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s of the match along with the corresponding batsman accordingly
        if pub_json['total_runs'] == 0:
            match_info['total_0s'] += 1
            # match_info[pub_json['batsman']]['total_0s'] += 1
        if pub_json['total_runs'] == 1:
            match_info['total_1s'] += 1
            # match_info[pub_json['batsman']]['total_1s'] += 1
        if pub_json['total_runs'] == 2:
            match_info['total_2s'] += 1
            # match_info[pub_json['batsman']]['total_2s'] += 1
        if pub_json['total_runs'] == 3:
            match_info['total_3s'] += 1
            # match_info[pub_json['batsman']]['total_3s'] += 1
        if pub_json['total_runs'] == 4:
            match_info['total_4s'] += 1
            # match_info[pub_json['batsman']]['total_4s'] += 1
        if pub_json['total_runs'] == 5:
            match_info['total_5s'] += 1
            # match_info[pub_json['batsman']]['total_5s'] += 1
        if pub_json['total_runs'] >= 6:
            match_info['total_6s'] += 1
            # match_info[pub_json['batsman']]['total_6s'] += 1
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
        if pub_json['total_runs'] == 0 and pub_json['inning'] == 1:
            match_info['total_0s_inn1'] += 1
        if pub_json['total_runs'] == 1 and pub_json['inning'] == 1:
            match_info['total_1s_inn1'] += 1
        if pub_json['total_runs'] == 2 and pub_json['inning'] == 1:
            match_info['total_2s_inn1'] += 1
        if pub_json['total_runs'] == 3 and pub_json['inning'] == 1:
            match_info['total_3s_inn1'] += 1
        if pub_json['total_runs'] == 4 and pub_json['inning'] == 1:
            match_info['total_4s_inn1'] += 1
        if pub_json['total_runs'] == 5 and pub_json['inning'] == 1:
            match_info['total_5s_inn1'] += 1
        if pub_json['total_runs'] >= 6 and pub_json['inning'] == 1:
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

        #   Update total 0s, 1s, 2s, 3s, 4s, 5s and 6s for the second innings accordingly
        if pub_json['total_runs'] == 0 and pub_json['inning'] == 2:
            match_info['total_0s_inn2'] += 1
        if pub_json['total_runs'] == 1 and pub_json['inning'] == 2:
            match_info['total_1s_inn2'] += 1
        if pub_json['total_runs'] == 2 and pub_json['inning'] == 2:
            match_info['total_2s_inn2'] += 1
        if pub_json['total_runs'] == 3 and pub_json['inning'] == 2:
            match_info['total_3s_inn2'] += 1
        if pub_json['total_runs'] == 4 and pub_json['inning'] == 2:
            match_info['total_4s_inn2'] += 1
        if pub_json['total_runs'] == 5 and pub_json['inning'] == 2:
            match_info['total_5s_inn2'] += 1
        if pub_json['total_runs'] >= 6 and pub_json['inning'] == 2:
            match_info['total_6s_inn2'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total extras and total wickets for the entire match
        if 'total_extras' not in match_info:
            match_info['total_extras'] = 0
        #     match_info[pub_json['bowler']]['total_extras'] = 0
        if 'total_wickets' not in match_info:
            match_info['total_wickets'] = 0
        #     match_info[pub_json['bowler']]['total_wickets'] = 0

        #   Update total extras and total wickets for the entire match
        if pub_json['extra_runs'] != 0:
            match_info['total_extras'] += pub_json['extra_runs']
            # match_info[pub_json['bowler']]['total_extras'] += pub_json['extra_runs']
        if pub_json['dismissal_kind'] != 'Not Dismissed':
            match_info['total_wickets'] += 1
            # match_info[pub_json['bowler']]['total_wickets'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total extras and total wickets for the first innings
        if 'total_extras_inn1' not in match_info:
            match_info['total_extras_inn1'] = 0
        if 'total_wickets_inn1' not in match_info:
            match_info['total_wickets_inn1'] = 0

        #   Update total extras and total wickets for the first innings
        if pub_json['extra_runs'] != 0 and pub_json['inning'] == 1:
            match_info['total_extras_inn1'] += pub_json['extra_runs']
        if pub_json['dismissal_kind'] != 'Not Dismissed' and pub_json['inning'] == 1:
            match_info['total_wickets_inn1'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize total extras and total wickets for the second innings
        if 'total_extras_inn2' not in match_info:
            match_info['total_extras_inn2'] = 0
        if 'total_wickets_inn2' not in match_info:
            match_info['total_wickets_inn2'] = 0

        #   Update total extras and total wickets for the second innings
        if pub_json['extra_runs'] != 0 and pub_json['inning'] == 2:
            match_info['total_extras_inn2'] += pub_json['extra_runs']
        if pub_json['dismissal_kind'] != 'Not Dismissed' and pub_json['inning'] == 2:
            match_info['total_wickets_inn2'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize and update balls bowled of a particular player if balls bowled
        if 'balls_bowled' not in match_info:
            match_info['balls_bowled'] = 0

        match_info['balls_bowled'] += 1
        #   -------------------------------------------------------------------------------------------------------    #

        #   -------------------------------------------------------------------------------------------------------    #
        #   Initialize or update number of wickets for a player if wicket taken
        # if pub_json['dismissal_kind'] != 'Not Dismissed':
        #     if 'wickets' in match_info[pub_json['bowler']]:
        #         match_info[pub_json['bowler']]['wickets'] += 1
        #     else:
        #         match_info[pub_json['bowler']]['wickets'] = 1
        #   -------------------------------------------------------------------------------------------------------    #

        # print("after",match_info)
        return match_info

    return {}


def lambda_handler(event, context):
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

            deliveries_info_response = get_response(es_config['es_deliveries_index'], currentEvent['UID'])

            match_info = update_match_info(currentEvent, deliveries_info_response)

            player_info_1, pid_1 = update_player_info(player_id_map, currentEvent, deliveries_info_response, 'batsman')
            player_info_2, pid_2 = update_player_info(player_id_map, currentEvent, deliveries_info_response, 'bowler')

            insert_into_es(currentEvent, es_config['es_deliveries_index'], currentEvent['UID'])

            insert_into_es(match_info, es_config['es_matches_index'], int(match_info['match_id']))

            print(player_info_1, pid_1)
            print(player_info_2, pid_2)
            insert_into_es(player_info_1, es_config['es_players_index'], pid_1)
            insert_into_es(player_info_2, es_config['es_players_index'], pid_2)

    # response = requests.post('http://34.227.172.158:3718/', json=json.dumps(currentEvent))


def manipulate_data(currentEvent):
    deliveries_info_response = get_response(es_config['es_deliveries_index'], currentEvent['UID'])
    match_info_response = get_response(es_config['es_matches_index'], currentEvent['match_id'])
    player_info_response1 = get_response(es_config['es_players_index'], player_id_map[currentEvent['batsman']])
    player_info_response2 = get_response(es_config['es_players_index'], player_id_map[currentEvent['bowler']])
    print(match_info_response)
    # print(player_info_response1)
    # print(player_info_response2)
    # exit(0)

    match_info = update_match_info(currentEvent, match_info_response)
    # print(json.dumps(match_info, indent=2))
    player_info_1, pid_1 = update_player_info(player_id_map, currentEvent, player_info_response1, 'batsman')
    # print(json.dumps(player_info_1, indent=2))
    player_info_2, pid_2  = update_player_info(player_id_map, currentEvent, player_info_response2, 'bowler')
    # print(json.dumps(player_info_2, indent=2))
    # exit(0)
    #
    # player_info_1, pid_1 = update_player_info(player_id_map, currentEvent, player_info_response1, 'batsman')
    # player_info_2, pid_2 = update_player_info(player_id_map, currentEvent, player_info_response2, 'bowler')

    insert_into_es(currentEvent, es_config['es_deliveries_index'], currentEvent['UID'])

    insert_into_es(match_info, es_config['es_matches_index'], int(match_info['id']))

    # print(player_info_1, pid_1)
    # print(player_info_2, pid_2)
    insert_into_es(player_info_1, es_config['es_players_index'], pid_1)
    insert_into_es(player_info_2, es_config['es_players_index'], pid_2)



with open('deliveries.json') as f:
  deliveries = json.load(f)
for each_ in deliveries:
    print(each_)
    manipulate_data(currentEvent= each_)
    # exit(0)



# ## matches load to ES
# with open('../data/matches/matches_latlong.json') as f:
#   matches = json.load(f)
# for each_ in matches:
#     print(each_)
#     # exit(0)
#     location = {}
#     location['lat'] = each_['latitude']
#     location['lon'] = each_['longitude']
#     each_.pop('latitude')
#     each_.pop('longitude')
#     each_['location'] = location
#     print(insert_into_es(each_,"matches", each_['id']))
#     # exit(0)

# ## Players load to ES
# with open('../data/players.json') as f:
#   players = json.load(f)
# print(type(players))
# print(players.keys())
# for each_ in players.keys():
#     print(players[each_])
#     # exit(0)
#     # location = {}
#     # location['lat'] = each_['latitude']
#     # location['lon'] = each_['longitude']
#     # each_.pop('latitude')
#     # each_.pop('longitude')
#     # each_['location'] = location
#     print(insert_into_es(players[each_],"players", players[each_]['uid']))