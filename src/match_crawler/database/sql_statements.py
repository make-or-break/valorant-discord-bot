from sqlalchemy import select
from sqlalchemy import update

import valorant
import match_crawler.database.sql_scheme as db


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
