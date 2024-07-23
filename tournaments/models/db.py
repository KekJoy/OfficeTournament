import enum
import uuid

from sqlalchemy import Column, UUID, String, DateTime, func, ARRAY, Integer, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import ENUM

from database import Base
from tournaments.models.utils import TournamentStatusENUM, GridTypeENUM


class Sport(Base):
    __tablename__ = "sport"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    sport_id = mapped_column(ForeignKey(Sport.id, ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    enroll_start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    enroll_end_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    grid = mapped_column(ForeignKey("grid.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    location = Column(String, nullable=False)
    admins_id = Column(ARRAY(UUID), nullable=False)
    players_id = Column(ARRAY(UUID), nullable=True)
    status = Column(ENUM(TournamentStatusENUM, name="tournament_status_enum", create_type=False), nullable=False,
                    default=TournamentStatusENUM.SCHEDULED)
    team_players_limit = Column(Integer, nullable=False)
    teams_limit = Column(Integer, nullable=False)


class Grid(Base):
    __tablename__ = "grid"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grid_type = Column(ENUM(GridTypeENUM, name="grid_type_enum", create_type=False), nullable=False,
                       default=GridTypeENUM.PLAYOFF)
    third_place_match = Column(Boolean, nullable=False, default=False)
