import json
import api

## Helpers for user data
def get_user_champion_winrate(user, champion):
    api.get_matchlists_by_account_id()

# In this function we are going to extract as much data as possible for a specific user 
def get_user_data(match, participant_id, team_id):
    ret = {}

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
        row = {**row, **team_data_0}

        team_data_1 = get_team_data(match, 1)
        team_data_1 = get_processed_data(team_data_1, 1)
        row = {**row, **team_data_1}

        data.append(row)

    return data

def get_processed_data(team_data, team):
    return {}