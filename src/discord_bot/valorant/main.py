import requests
import json


def get_player(Username, Tagline):
    """
    Get the json data of a player.
    """

    api_url = "https://api.henrikdev.xyz/valorant/v2/mmr/eu/"+Username+"/"+Tagline
    response = requests.get(api_url)
    data = response.json()

    return(data)


def get_player_by_puuid(puuid):
    """
    Get the json data of a player by puuid.
    """

    api_url = "https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/eu/"+puuid
    response = requests.get(api_url)
    data = response.json()

    return(data)


def get_elo(data):
    """
    Get the elo of a player.
    """

    return(data["data"]["current_data"]["elo"])


def get_rank(data):
    """
    Get the rank of a player.
    """

    return (data["data"]["current_data"]["currenttierpatched"])


def get_rank_tier(data):
    """
    Get the rank tier of a player.
    """

    return (data["data"]["current_data"]["currenttier"])


if __name__ == "__main__":
    # libary is meant to be used as a module
    # so this is only used for testing
    data = get_player("MayNiklas", "Niki")
    print(get_elo(data))
    print(get_rank_tier(data))
    print(get_rank(data))
