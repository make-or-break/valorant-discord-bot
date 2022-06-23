from sqlalchemy import select
from sqlalchemy import update

import sql_scheme as db


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


def get_player(id, session=db.open_session()):
    """
    Get the player from the database
    """
    return session.query(db.Players).filter(db.Players.id == id).first()
