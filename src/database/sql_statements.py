from sqlalchemy import select
from sqlalchemy import update

import database.sql_scheme as db

################################################################################
# db statements relevant to the player table used by the discord-bot


def add_player(id, elo, rank, rank_tier, username, tagline, puuid, session=db.open_session()):
    """
    Add an entry to the players database
    """
    entry = db.Player(id=id, username=username, elo=elo,
                       rank=rank, rank_tier=rank_tier, tagline=tagline, puuid=puuid)
    print(
        f'Add to database! id: {id} Username: {username} - elo: {elo} - rank: {rank} - rank_tier: {rank_tier} - tagline: {tagline} - puuid: {puuid}')
    session.add(entry)
    session.commit()


def update_player(id, elo, rank, rank_tier, username, tagline, puuid, session=db.open_session()):
    """
    Update the player in the database
    """
    session.query(db.Player).filter(db.Player.id == id).update({
        'elo': elo,
        'rank': rank,
        'rank_tier': rank_tier,
        'tagline': tagline,
        'username': username,
        'puuid': puuid
    })
    session.commit()


def get_all_players(session=db.open_session()):
    """
    Get all players from the database
    """
    return session.query(db.Player).all()


def get_player(id, session=db.open_session()):
    """
    Get the player from the database
    """
    return session.query(db.Player).filter(db.Player.id == id).first()


def player_exists(id, session=db.open_session()):
    """
    Check if the player exists in the database
    """
    return session.query(db.Player).filter(db.Player.id == id).first() is not None

################################################################################
# db statements relevant to the matches table used by the match crawler


def add_match(puuid, match_id, match_start, match_length, match_rounds, match_map, session=db.open_session()):
    """
    Add a match to the DB.
    """

    entry = db.Match(
        puuid=puuid,
        match_id=match_id,
        match_start=match_start,
        match_length=match_length,
        match_rounds=match_rounds,
        match_map=match_map
    )

    print(
        f'Add match to database! puuid: {puuid} - match_id: {match_id} - match_start: {match_start} - match_length: {match_length} - match_rounds: {match_rounds} - match_map: {match_map}')
    session.add(entry)
    session.commit()


def match_exists(puuid, match_id, session=db.open_session()):
    """
    Check if the match exists in the database
    """
    return session.query(db.Match).filter(db.Match.puuid == puuid, db.Match.match_id == match_id).first() is not None
