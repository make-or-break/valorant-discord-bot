import valorant
from match_crawler.database import sql_statements as db


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
            db.add_match(puuid, match, mmr_data)


def check_new_matches():
    '''
    check all players in DB for untracked matches
    '''

    for player in db.get_tracked_users():
        matches_by_puuid(player.puuid)


if __name__ == '__main__':
    '''
    for testing this module isolated
    '''

    # creates DB entry if not existent
    db.update_tracking(
        'd515e2d5-b50e-5c77-a79e-eeb46dbe488a', True)

    # check if user got created successfully
    # also make sure to check if tracked is set to True
    # check if False returns nothing!
    print(db.get_tracked_users())

    # check if match crawling works
    # should return nothing the second run!
    check_new_matches()
