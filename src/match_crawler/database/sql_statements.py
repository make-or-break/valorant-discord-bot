from sqlalchemy import select
from sqlalchemy import update

import valorant
from ..database import sql_scheme as db


#############################################################################################
# User handling
#############################################################################################

def add_user(puuid, tracked, session=db.open_session()):
    """
    Add a user to the DB.
    """

    if user_exists(puuid, session):
        print(f'User {puuid} already exists in DB!')
        pass
    else:
        entry = db.User(puuid=puuid, tracked=tracked)
        session.add(entry)
        session.commit()
        print(f'Added user to database: {puuid} - {tracked}')


def update_tracking(puuid, tracked, session=db.open_session()):
    """
    Update the tracking status of a user in the DB.
    Create the user if it does not exist.
    """

    if user_exists(puuid, session):
        entry = session.query(db.User).filter(db.User.puuid == puuid).first()
        entry.tracked = tracked
        session.commit()
        print(f'Updated tracking status of user {puuid} to {tracked}')
    else:
        add_user(puuid, tracked)
        pass


def user_exists(puuid, session=db.open_session()):
    """
    Check if the user exists in the database
    """
    return session.query(db.User).filter(db.User.puuid == puuid).first() is not None


def get_tracked_users(session=db.open_session()):
    """
    Get all tracked users from the DB.
    """
    return session.query(db.User).filter(db.User.tracked == True).all()

#############################################################################################
# Match handling
#############################################################################################


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
