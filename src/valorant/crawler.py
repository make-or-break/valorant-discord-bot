from sqlalchemy import select
from sqlalchemy import update

import valorant
from database import sql_scheme as db


################################################################################
# db statements relevant for this file
################################################################################
# explanation:
# those sql statements can hold a lot of parameters!
# passing 10 values to a proxy function is not well readable
# -> it makes more sense to execute the statement directly
# we also could import valorant in databases
################################################################################

def match_exists(puuid, match_id, session=db.open_session()):
    """
    Check if the match exists in the database
    """
    return session.query(db.Match).filter(db.Match.puuid == puuid, db.Match.match_id == match_id).first() is not None


def add_match(puuid, match_id, mmr_data, session=db.open_session()):
    """
    Add a match to the DB.
    """

    # get match stats
    match_stats = valorant.get_match_json(match_id)

    entry = db.Match(
        puuid=puuid,
        match_id=match_id,
        match_start=valorant.get_game_start(match_stats),
        match_length=valorant.get_game_length(match_stats),
        match_rounds=valorant.get_rounds_played(match_stats),
        match_mmr_change=valorant.get_mmr_change(
            mmr_data, valorant.get_game_start(match_stats)),
        match_elo=valorant.get_mmr_elo(
            mmr_data, valorant.get_game_start(match_stats)),
        match_map=valorant.get_map(match_stats)
    )

    print(
        f'Add match to database!\n',
        f'puuid: {puuid}\n',
        f'match_id: {match_id}\n',
        f'match_start: {valorant.get_game_start(match_stats)}\n',
        f'match_length: {valorant.get_game_length(match_stats)}\n',
        f'match_rounds: {valorant.get_rounds_played(match_stats)}\n',
        f'match_mmr_change: {valorant.get_mmr_change(mmr_data, valorant.get_game_start(match_stats))}\n',
        f'match_elo: {valorant.get_mmr_elo(mmr_data, valorant.get_game_start(match_stats))}\n',
        f'match_map: {valorant.get_map(match_stats)}\n'
    )

    session.add(entry)
    session.commit()


################################################################################
# code handling the crawling process
################################################################################


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
        if match_exists(puuid, match):
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
