from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from tournaments.models.utils import GridTypeENUM, TournamentStatusENUM


class BriefUserSchema(BaseModel):
    id: UUID
    full_name: str
    avatar_id: int


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


class GetTournamentPageSchema(GetTournamentSchema):
    admin: BriefUserSchema
    players_count: int
    sport_title: str


class TournamentFiltersSchema(BaseModel):
    sport_id: Optional[UUID] | None = None
    start_time_from: Optional[datetime] | None = None
    start_time_to: Optional[datetime] | None = None
    status: Optional[TournamentStatusENUM] | None = None
    is_solo: Optional[bool] | None = None


class TournamentPlayersSchema(TournamentFiltersSchema):
    players: List[BriefUserSchema]


class CreateSportSchema(BaseModel):
    name: str


class GetSportSchema(CreateSportSchema):
    id: UUID
