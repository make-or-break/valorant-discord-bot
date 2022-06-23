import requests
import json


def get_elo(Username, Tagline):
    """
    Get the elo of a player.
    """

    api_url = "https://api.henrikdev.xyz/valorant/v2/mmr/eu/"+Username+"/"+Tagline

    # get the data from the api
    response = requests.get(api_url)
    data = response.json()

    return(data["data"]["current_data"]["elo"])


def get_rank(elo):
    """
    Get the rank of a player.
    """

    if elo < 1000:
        return("Unranked")


if __name__ == "__main__":
    print(get_rank((get_elo("MayNiklas", "Niki"))))
