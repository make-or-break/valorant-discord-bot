import time

import valorant
from database import sql_statements as db


def add_match(puuid, match_id, mmr_data):
    '''
    Add a match to the DB
    '''

    # get match stats
    match_stats = valorant.get_match_json(match_id)

    db.add_match(
        puuid,
        match_id,
        valorant.get_game_start(match_stats),
        valorant.get_game_length(match_stats),
        valorant.get_rounds_played(match_stats),
        valorant.get_mmr_change(
            mmr_data, valorant.get_game_start(match_stats)),
        valorant.get_mmr_elo(mmr_data, valorant.get_game_start(match_stats)),
        valorant.get_map(match_stats)
    )


def matches_by_puuid(puuid):
    '''
    Go through match history of player and add matches to DB
    '''

    # get last 5 matches of a player
    player_matches = valorant.get_matches_json_by_puuid(puuid)

    # get mmr history
    # we request it here, so we only have to request it once for all 5 matches
    mmr_data = valorant.get_mmr_json(puuid)

    # iterate through the matches
    for match in valorant.get_match_ids(player_matches):

        # check if match exists in DB
        if db.match_exists(puuid, match):
            # match already exists in DB -> do nothing
            pass

        else:
            # match is new to DB -> add it
            add_match(puuid, match, mmr_data)


def check_new_matches():
    '''
    check all players in DB for untracked matches
    '''

    for player in db.get_all_players():
        matches_by_puuid(player.puuid)


if __name__ == '__main__':
    # for testing this method isolated
    matches_by_puuid('d515e2d5-b50e-5c77-a79e-eeb46dbe488a')
