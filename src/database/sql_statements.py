from sqlalchemy import select
from sqlalchemy import update

import database.sql_scheme as db


def add_player(id, username, elo, rank, rank_tier, tagline, puuid, session=db.open_session()):
    """
    Add an entry to the players database
    """
    entry = db.Players(id=id, username=username, elo=elo,
                       rank=rank, rank_tier=rank_tier, tagline=tagline, puuid=puuid)
    print(
        f'Add to database! id: {id} Username: {username} - elo: {elo} - rank: {rank} - rank_tier: {rank_tier} - tagline: {tagline} - puuid: {puuid}')
    session.add(entry)
    session.commit()


def update_player(id, elo, rank, rank_tier, tagline, username, session=db.open_session()):
    """
    Update the player in the database
    """
    session.query(db.Players).filter(db.Players.id == id).update({
        'elo': elo,
        'rank': rank,
        'rank_tier': rank_tier,
        'tagline': tagline,
        'username': username
    })
    session.commit()


def get_player(id, session=db.open_session()):
    """
    Get the player from the database
    """
    return session.query(db.Players).filter(db.Players.id == id).first()

def add_role(id, name, color, elo, session=db.open_session()):
    """
    Add a role to the database
    """
    entry = db.Roles(id=id, name=name, color=color, elo=elo)
    print(
        f'Add to database! id: {id} Name: {name} - color: {color} - elo: {elo}')
    session.add(entry)
    session.commit()

def update_role(id, name, color, elo, session=db.open_session()):
    """
    Update the role in the database
    """
    session.query(db.Roles).filter(db.Roles.id == id).update({
        'name': name,
        'color': color,
        'elo': elo
    })
    session.commit()

def get_role(id, session=db.open_session()):
    """
    Get the role from the database
    """
    return session.query(db.Roles).filter(db.Roles.id == id).first()

def get_role_by_rank_tier(rank_tier, session=db.open_session()):
    """
    Get the role from the database
    """
    return session.query(db.Roles).filter(db.Roles.rank_tier == rank_tier).first()