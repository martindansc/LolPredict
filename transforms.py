import json
import api

## Helpers for user data
def get_if_account_won_match(match, user):
    first_team = False
    for i in range(5):
        if(match["participantIdentities"][i]["player"]["currentAccountId"] == user):
            first_team = True

    first_team_wins = match["teams"][0]["win"] == "Win"

    return (first_team and first_team_wins) or (not first_team and not first_team_wins) 

def get_player_champion_winrate(user, champion):
    ret = {}
    matches = api.get_matchlists_by_account_id(user, {"champion" : champion})

    num_wins = 0
    num_matches = 0
    for match in matches["matches"]:
        recorded_match = api.get_match_by_id(match["gameId"])
        if(recorded_match):
            if(get_if_account_won_match(recorded_match, user)):
                num_wins += 1
            num_matches += 1

    ret["num_matches"] = num_matches
    ret["num_wins"] = num_wins
    if matches == 0:
        ret["win_ratio"] = 0.5
    else:
        ret["win_ratio"] = ret["num_wins"]/ret["num_matches"]

    return ret

# In this function we are going to extract as much data as possible for a specific user 
def get_user_data(match, participant_id, team_id):
    participant = match["participants"][participant_id - 1]
    participant_identity = match["participantIdentities"][participant_id - 1]["player"]
    ret = {}
    
    ret = {**ret, **get_player_champion_winrate(participant_identity["currentAccountId"], participant["championId"])}

    return ret

def get_team_data(match, team):
    team_data = []
    for participant_id in range(1 + 5*team, 6+5*team):
        user_data = get_user_data(match, participant_id, 0)
        team_data.append(user_data)

    return team_data
    

def generate_players_match_data():
    data = []
    matches = api.get_matches()
    for match in matches:

        row = {}
        
        team_data_0 = get_team_data(match, 0)
        team_data_0 = get_processed_data(team_data_0, 0)
        print(team_data_0)
        row = {**row, **team_data_0}

        team_data_1 = get_team_data(match, 1)
        team_data_1 = get_processed_data(team_data_1, 1)
        row = {**row, **team_data_1}

        data.append(row)

    return data

def get_processed_data(team_data, team):
    return {}