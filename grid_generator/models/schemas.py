from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from tournaments.models.utils import GridTypeENUM


class GameSchema(BaseModel):
    id: UUID
    score: List[int] = Field(min_length=2, max_length=2)


class GridUserSchema(BaseModel):
    id: UUID
    full_name: str


class UpdateScoreSchema(BaseModel):
    score: List[int] = Field(min_length=2, max_length=2)


class BasicMatchSchema(BaseModel):
    id: UUID
    players: List[GridUserSchema | None] = Field(min_length=2, max_length=2)
    score: List[int] = Field(min_length=2, max_length=2)


class MatchSchema(BasicMatchSchema):
    games: list[GameSchema]


class WrappedMatchSchema(BaseModel):
    match: MatchSchema


class RoundSchema(BaseModel):
    id: UUID
    round_number: int
    matches: List[BasicMatchSchema]


class GridSchema(BaseModel):
    id: UUID
    grid_type: GridTypeENUM
    rounds: List[RoundSchema]
    third_place_match: Optional[BasicMatchSchema]


class GridSchemaWrapped(BaseModel):
    grid: GridSchema
