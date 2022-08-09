import os
import sys

import sqlalchemy
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

if not os.path.exists('data/'):
    os.mkdir('data/')

try:
    engine = create_engine('sqlite:///data/players.db')
    connection = engine.connect()
    Base = declarative_base()

    class Player(Base):
        __tablename__ = 'players'
        elo = Column(Integer)
        id = Column(Integer, primary_key=True)
        puuid = Column(String)
        rank = Column(String)
        rank_tier = Column(Integer)
        tagline = Column(String)
        username = Column(String)

        def __repr__(self):
            return f"id='{self.id}', username='{self.username}', tagline='{self.tagline}', elo='{self.elo}', rank='{self.rank}', rank_tier='{self.rank_tier}, puuid='{self.puuid}'"

    class Settings(Base):
        __tablename__ = 'settings'
        id = Column(Integer, primary_key=True)
        public_elo = Column(Boolean)

        def __repr__(self):
            return f"id='{self.id}', public_elo='{self.public_elo}'"

    Base.metadata.create_all(engine)

    @event.listens_for(Base.metadata, 'after_create')
    def receive_after_create(target, connection, tables, **kw):
        """listen for the 'after_create' event"""
        logger.info('A table was created' if tables else 'No table was created')
        print('A table was created' if tables else 'No table was created')

    def open_session() -> sqlalchemy.orm.Session:
        """
        :return: new active session
        """
        return sessionmaker(bind=engine)()

except:
    print('An exception while connecting to the DB has occurred')
    sys.exit()
