import uuid

from sqlalchemy import Column, UUID, ARRAY, Integer, ForeignKey
from sqlalchemy.orm import mapped_column

from database import Base
from tournaments.models.db import Grid


class Round(Base):
    __tablename__ = 'round'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_number = Column(Integer, nullable=False)
    game_count = Column(Integer, nullable=False)
    grid_id = mapped_column(ForeignKey(Grid.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class Match(Base):
    __tablename__ = 'match'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_match_number = Column(Integer, nullable=False)
    queue_match_number = Column(Integer, nullable=False)  # for if queue items are movable
    round_id = mapped_column(ForeignKey(Round.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    players_id = Column(ARRAY(UUID), nullable=False)
    score = Column(ARRAY(Integer), nullable=False)
    winner_id = Column(UUID(as_uuid=True), nullable=True)


class Game(Base):
    __tablename__ = 'game'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = mapped_column(ForeignKey(Match.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    game_number = Column(Integer, nullable=False)
    score = Column(ARRAY(Integer), nullable=False)
