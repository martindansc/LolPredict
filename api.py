import requests
import json
import os
import time

STATIC_MATCH_URL = "https://s3-us-west-1.amazonaws.com/riot-developer-portal/seed-data/matches"
LOL_API_BASE_URL = ".api.riotgames.com"
API_KEY = {'api_key': os.getenv("KEY")}

## Core
def make_request_lol_api(path, page = 1):
    time.sleep(0.2)
    payload = {**API_KEY, **{"page" : page}}
    return (requests.get("https://" + os.getenv("REGION") + LOL_API_BASE_URL + path, payload)).json()


def make_cacheable_request_lol_api(path, page = 1):
    result = {}

    filename = "api-files" + path + "_" + str(page) + ".json"
    exists = os.path.isfile(filename)
    if not exists:
        result = make_request_lol_api(path)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, "w") as json_file:  
            json.dump(result, json_file)
    else:
        with open(filename) as json_file:  
            result = json.load(json_file)
    
    return result


## Interface
def get_league_entries(tier, division, page):
    return make_cacheable_request_lol_api('/lol/league/v4/entries/RANKED_SOLO_5x5/' + tier + "/" + division, page)

def get_matches():
    
    random_pages = [1,145,248,384,64,724,562,678,895,736]
    
    for i in random_pages:
        exists = os.path.isfile("api-files/matches/data" + str(i) + ".json")
        if not exists:
            print("Generating file: data" + str(i) + ".json")

            url = STATIC_MATCH_URL + str(i) + '.json'

            result = requests.get(url)

            with open("api-files/matches/data" + str(i) + ".json", "w") as json_file:  
                json.dump(result.json(), json_file)
    ret = []
    for i in range(1, 11):
        with open("api-files/matches/data" + str(i) + ".json") as json_file:  
            matches = (json.load(json_file))["matches"]
            ret = ret + matches
    
    return ret

def get_summoner_by_name(name):
    return make_cacheable_request_lol_api('/lol/summoner/v4/summoners/by-name/' + name)