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


def delete_player(id, session=db.open_session()):
    """
    Delete the player from the database
    """
    session.query(db.Player).filter(db.Player.id == id).delete()
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


def add_settings(id, public_elo=False, session=db.open_session()):
    """
    Add an entry to the settings database
    """
    entry = db.Settings(id=id, public_elo=public_elo)
    print(
        f'Add to settings db! id: {id} - public_elo: {public_elo}')
    session.add(entry)
    session.commit()


def update_settings(id, public_elo, session=db.open_session()):
    """
    Update the settings in the database
    """
    session.query(db.Settings).filter(db.Settings.id == id).update({
        'public_elo': public_elo
    })
    session.commit()


def get_settings(id, session=db.open_session()):
    """
    Get the settings from the database
    """
    return session.query(db.Settings).filter(db.Settings.id == id).first()


def settings_exists(id, session=db.open_session()):
    """
    Check if the settings exists in the database
    """
    return session.query(db.Settings).filter(db.Settings.id == id).first() is not None
