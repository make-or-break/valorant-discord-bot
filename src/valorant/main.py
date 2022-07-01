import json

import requests

# API documentation:
# https://docs.henrikdev.xyz/valorant.html


###############################################################################
# code related to getting player stats

def get_player_json(Username, Tagline):
    """
    Get the json data of a player.
    """

    api_url = 'https://api.henrikdev.xyz/valorant/v2/mmr/eu/'+Username+'/'+Tagline

    response = requests.get(api_url)

    if response.status_code == 200:
        return(response.json())
    else:
        return(None)


def get_player_json_by_puuid(puuid):
    """
    Get the json data of a player by puuid.
    """

    api_url = 'https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/eu/'+puuid
    response = requests.get(api_url)
    data = response.json()

    return(data)


def get_elo(data):
    """
    Get the elo of a player.
    """

    return(data['data']['current_data']['elo'])


def get_rank(data):
    """
    Get the rank of a player.
    """

    return (data['data']['current_data']['currenttierpatched'])


def get_rank_tier(data):
    """
    Get the rank tier of a player.
    """

    return (data['data']['current_data']['currenttier'])


def get_puuid(data):
    """
    Get the puuid of a player.
    """

    return (data['data']['puuid'])


###############################################################################
# code related to getting match history

def get_matches_json(Username, Tagline):
    """
    Get the last 5 matches that where played by this user
    """

    api_url = 'https://api.henrikdev.xyz/valorant/v3/matches/eu/' + \
        Username+'/'+Tagline+'?filter=competitive'

    response = requests.get(api_url)

    if response.status_code == 200:
        return(response.json())
    else:
        return(None)


def get_matchid(data):
    """
    Get the matchid of the last match.
    """

    return (data['data'][0]['metadata']['matchid'])


def get_match_ids(data):
    """
    Get the matchids of the last 5 matches.
    """

    ids = []
    for i in data['data']:
        ids.append(i['metadata']['matchid'])
    return ids


###############################################################################
# code related to getting match stats

def get_match_json(matchid):
    """
    Get the match stats of a match.
    """

    api_url = 'https://api.henrikdev.xyz/valorant/v2/match/' + matchid

    response = requests.get(api_url)

    if response.status_code == 200:
        return(response.json())
    else:
        return(None)


def get_match_metadata(data):
    """
    Get the metadata of a match
    """

    return (data['data']['metadata'])


def get_game_start(data):
    """
    Get the time of the start of the last match.
    """

    return (data['data']['metadata']['game_start'])


def get_game_length(data):
    """
    Get the length of the last match (in milliseconds).
    """

    return (data['data']['metadata']['game_length'])


def get_rounds_played(data):
    """
    Get the length of the last match (in rounds).
    """

    return (data['data']['metadata']['rounds_played'])


def get_map(data):
    """
    Get the map of the last match.
    """

    return (data['data']['metadata']['map'])

###############################################################################


if __name__ == '__main__':
    # libary is meant to be used as a module
    # so this is only used for testing
    data = get_player_json('MayNiklas', 'Niki')
    print(data)
