from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from tournaments.models.utils import GridTypeENUM, TournamentStatusENUM


class CreateTournamentSchema(BaseModel):
    title: str
    description: Optional[str] | None = None
    sport_id: UUID
    start_time: datetime
    enroll_start_time: datetime
    enroll_end_time: datetime
    grid_type: GridTypeENUM
    location: str
    admins_id: List[UUID]
    team_players_limit: int
    teams_limit: int

    class Config:
        use_enum_values = True
        from_attributes = True


class GetTournamentSchema(CreateTournamentSchema):
    id: UUID
    players_id: List[UUID] | None = None
    status: TournamentStatusENUM


class PatchTournamentSchema(BaseModel):
    title: Optional[str] | None = None
    description: Optional[str] | None = None
    sport_id: Optional[UUID] | None = None
    start_time: Optional[datetime] | None = None
    enroll_start_time: Optional[datetime] | None = None
    enroll_end_time: Optional[datetime] | None = None
    location: Optional[str] | None = None


class TournamentResponse(BaseModel):
    total_count: int
    tournaments: List[GetTournamentSchema]


class TournamentFiltersSchema(BaseModel):
    sport_id: Optional[UUID] | None = None
    start_time_from: Optional[datetime] | None = None
    start_time_to: Optional[datetime] | None = None
    status: Optional[List[TournamentStatusENUM]] | None = None
    is_solo: Optional[bool] | None = None


class CreateSportSchema(BaseModel):
    name: str


class GetSportSchema(CreateSportSchema):
    id: UUID
