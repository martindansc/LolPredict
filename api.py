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
    time.sleep(0.3)


def make_request_lol_api(path, params = {}, retries = 1):
    wait_time()
    print("Making resquest: " + path)
    payload = {**API_KEY, **params}
    response =  (requests.get("https://" + os.getenv("REGION") + LOL_API_BASE_URL + path, payload))
    if response.status_code != 200:
        print("Error in request: " + response.reason)
        if response.status_code != 404:
            if retries > 5:
                exit()
            else:
                time.sleep(retries*10)
                retries += 1
                return make_request_lol_api(path, params, retries)
    return response.json()


def make_cacheable_request_lol_api(path, params = {}):
    result = {}

    str_page = ""
    for key in params:
        str_page += "_" + str(params[key])

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

    if("status" in result):
        return False
    
    return result


## Interface
def get_matches():
    
    random_pages = [1,145,248,384,64,724,562,678,895,736]
    
    for random_page in random_pages:
        exists = os.path.isfile("api-files/matches/data" + str(random_page) + ".json")
        if not exists:
            matches = []
            league = get_league_entries(os.getenv("TIER"), os.getenv("DIVISION"), random_page)
            for j in range(20):
                player = league[j]
                account = get_summoner_by_id(player["summonerId"])
                summoner_games = get_matchlists_by_account_id(account["accountId"])
                matches.append(get_match_by_id(summoner_games["matches"][0]["gameId"]))

            with open("api-files/matches/data" + str(random_page) + ".json", "w") as json_file:  
                json.dump(matches, json_file)
    ret = []
    for random_page in random_pages:
        with open("api-files/matches/data" + str(random_page) + ".json") as json_file:  
            matches = (json.load(json_file))
            ret = ret + matches
    return ret

def get_summoner_by_name(name):
    return make_cacheable_request_lol_api('/lol/summoner/v4/summoners/by-name/' + name)

def get_summoner_by_id(id):
    return make_cacheable_request_lol_api('/lol/summoner/v4/summoners/' + id)

def get_matchlists_by_account_id(id, filters = {}):
    return make_cacheable_request_lol_api('/lol/match/v4/matchlists/by-account/' + id, {"queue" : 420, "endIndex" : 20, **filters})

def get_match_by_id(id):
    return make_cacheable_request_lol_api('/lol/match/v4/matches/' + str(id))
    
def get_league_entries(tier, division, page):
    return make_cacheable_request_lol_api('/lol/league/v4/entries/RANKED_SOLO_5x5/' + tier + "/" + division, {"page" : page})
