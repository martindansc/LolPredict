import requests
import json
import os
import time

STATIC_MATCH_URL = "https://s3-us-west-1.amazonaws.com/riot-developer-portal/seed-data/matches"
LOL_API_BASE_URL = ".api.riotgames.com"
API_KEY = {'api_key': os.getenv("KEY")}
API_CALLS_COUNTER = 0

## Core
def wait_time():
    global API_CALLS_COUNTER
    if API_CALLS_COUNTER >= 90:
        time.sleep(60)
        API_CALLS_COUNTER = 0
    API_CALLS_COUNTER += 1
    time.sleep(0.2)


def make_request_lol_api(path, params = {}):
    wait_time()
    payload = {**API_KEY, **params}
    response =  (requests.get("https://" + os.getenv("REGION") + LOL_API_BASE_URL + path, payload))
    if response.status_code != 200:
        print(response)
        exit()
    return response.json()


def make_cacheable_request_lol_api(path, params = {}):
    result = {}

    str_page = ""
    if("page" in params):
        str_page = "_" + str(params["page"])

    filename = "api-files" + path + str_page + ".json"
    exists = os.path.isfile(filename)
    if not exists:
        result = make_request_lol_api(path, params)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w") as json_file:  
            json.dump(result, json_file)
    else:
        with open(filename) as json_file:  
            result = json.load(json_file)
    
    return result


## Interface
def get_matches():
    
    random_pages = [1,145,248,384,64,724,562,678,895,736]
    
    for i in random_pages:
        exists = os.path.isfile("api-files/matches/data" + str(i) + ".json")
        if not exists:
            matches = []
            league = get_league_entries(os.getenv("TIER"), os.getenv("DIVISION"), i)
            for j in range(10):
                player = league[j]
                account = get_summoner_by_id(player["summonerId"])
                summoner_games = get_matchlists_by_account_id(account["accountId"])
                matches.append(get_match_by_id(summoner_games["matches"][0]["gameId"]))

            with open("api-files/matches/data" + str(i) + ".json", "w") as json_file:  
                json.dump(matches, json_file)
    ret = []
    for i in random_pages:
        with open("api-files/matches/data" + str(i) + ".json") as json_file:  
            matches = (json.load(json_file))
            ret = ret + matches
    
    return ret

def get_summoner_by_name(name):
    return make_cacheable_request_lol_api('/lol/summoner/v4/summoners/by-name/' + name)

def get_summoner_by_id(id):
    return make_cacheable_request_lol_api('/lol/summoner/v4/summoners/' + id)

def get_matchlists_by_account_id(id):
    return make_cacheable_request_lol_api('/lol/match/v4/matchlists/by-account/' + id, {"queue" : 420})

def get_match_by_id(id):
    return make_cacheable_request_lol_api('/lol/match/v4/matches/' + str(id))
    
def get_league_entries(tier, division, page):
    return make_cacheable_request_lol_api('/lol/league/v4/entries/RANKED_SOLO_5x5/' + tier + "/" + division, {"page" : page})
