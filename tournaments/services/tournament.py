import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Query

from auth.repository import UserRepository
from tournaments.models.schemas import CreateTournamentSchema, GetTournamentSchema, TournamentFiltersSchema
from tournaments.repository import SportRepository, TournamentRepository, GridRepository

tournament_router = APIRouter(prefix='/tournament', tags=['tournaments'])


@tournament_router.post("/create", response_model=uuid.UUID)
async def create_tournament(tournament: CreateTournamentSchema) -> uuid.UUID:
    """Создание турнира"""
    if not await SportRepository().find_one(tournament.sport_id):
        raise HTTPException(status_code=400, detail="The sport does not exist in the system.")
    if not tournament.enroll_start_time < tournament.enroll_end_time <= tournament.start_time:
        raise HTTPException(status_code=400, detail="Incorrect time frame of the tournament is specified.")
    if not await UserRepository().find_one(tournament.admins_id[0]):
        raise HTTPException(status_code=400, detail="The ID of the User assigned to the role of "
                                                    "tournament administrator does not exist in the system.")
    if tournament.team_players_limit and tournament.teams_limit <= 0:
        raise HTTPException(status_code=400, detail="Incorrect number of players when creating a tournament.")
    grid_id = await GridRepository().add_one({"grid_type": f"{tournament.grid_type}"})
    tournament_dict = tournament.model_dump()
    del tournament_dict["grid_type"]
    tournament_dict["grid"] = grid_id
    result = await TournamentRepository().add_one(tournament_dict)
    return result


@tournament_router.post("/filters", response_model=List[GetTournamentSchema])
async def get_all_tournaments(filters: TournamentFiltersSchema,
                              page: int = Query(ge=1, default=1),
                              size: int = Query(ge=1, le=100)) -> List[GetTournamentSchema]:
    """Получить турниры"""
    offset_min = (page - 1) * size
    offset_max = page * size

    tournaments = await TournamentRepository().filter_tournaments(filters.model_dump())
    result = []
    for trnmt in tournaments:
        grid = await GridRepository().get_one(trnmt.grid)
        grid_type = grid.grid_type if grid else None

        tournament_dict = trnmt.__dict__
        tournament_dict['grid_type'] = grid_type
        del tournament_dict['grid']
        result.append(GetTournamentSchema(**tournament_dict))
    return result[offset_min:offset_max]


@tournament_router.get("/{id}", response_model=GetTournamentSchema)
async def get_tournament(id: uuid.UUID) -> GetTournamentSchema:
    """Получить турнир по ID"""
    tournament = await TournamentRepository().get_one(record_id=id)
    if not tournament:
        raise HTTPException(status_code=400, detail="The tournament with the transferred ID does not exist.")
    grid = await GridRepository().get_one(tournament.grid)
    grid_type = grid.grid_type if grid else None

    tournament_dict = tournament.__dict__
    tournament_dict['grid_type'] = grid_type
    del tournament_dict['grid']

    return GetTournamentSchema(**tournament_dict)


@tournament_router.post("/{id}/enroll/{user_id}")
async def enroll(id: uuid.UUID, user_id: uuid.UUID) -> GetTournamentSchema:
    """Участвовать в турнире"""
    # TODO: check authorization
    tournament = await TournamentRepository().get_one(record_id=id)
    players_id = tournament.players_id or []
    if user_id in players_id:
        raise HTTPException(status_code=400, detail="The user is already enrolled.")
    if len(players_id) >= tournament.teams_limit:
        raise HTTPException(status_code=400, detail="The players limit has been reached.")
    if not await UserRepository().find_one(record_id=user_id):
        raise HTTPException(status_code=400, detail="User doesn't exist.")
    players_id.append(user_id)
    await TournamentRepository().update_one(record_id=id, data={"players_id": players_id})
    return GetTournamentSchema(**tournament.__dict__)
