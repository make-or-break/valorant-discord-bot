import valorant
from database import sql_statements as db


def matches():
    '''
    Go through all players in the DB and add their match ID's to the DB
    '''

    # go through all players in the DB
    for player in db.get_all_players():

        # get last 5 matches of a player
        player_matches = valorant.get_matches_json_by_puuid(player.puuid)

        # iterate through the matches
        for match in valorant.get_match_ids(player_matches):

            # check if match exists in DB
            if db.match_exists(player.puuid, match):
                # match already exists in DB -> do nothing
                pass

            else:
                # match is new to DB -> add it
                db.add_match(player.puuid, match)


if __name__ == '__main__':
    matches()
