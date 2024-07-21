import uuid
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Query

from auth.repository import UserRepository
from tournaments.models.schemas import CreateTournamentSchema, GetTournamentSchema, TournamentFiltersSchema, \
    GetTournamentPageSchema, BriefUserSchema, TournamentResponse, PatchTournamentSchema
from tournaments.repository import SportRepository, TournamentRepository, GridRepository
from tournaments.models.utils import TournamentStatusENUM

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


@tournament_router.post("/filters", response_model=TournamentResponse)
async def get_all_tournaments(filters: TournamentFiltersSchema,
                              page: int = Query(ge=1, default=1),
                              size: int = Query(ge=1, le=100)) -> TournamentResponse:
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

    total_count = len(result)
    return TournamentResponse(total_count=total_count, tournaments=result[offset_min:offset_max])


@tournament_router.get("/{id}", response_model=GetTournamentPageSchema)
async def get_tournament(id: uuid.UUID) -> GetTournamentPageSchema:
    """Получить турнир по ID"""
    tournament = await TournamentRepository().get_one(record_id=id)
    if not tournament:
        raise HTTPException(status_code=400, detail="The tournament with the transferred ID does not exist.")
    grid = await GridRepository().get_one(tournament.grid)
    grid_type = grid.grid_type if grid else None

    tournament_dict = tournament.__dict__
    tournament_dict['grid_type'] = grid_type
    del tournament_dict['grid']

    admin = await UserRepository().get_one(record_id=tournament.admins_id[0])
    sport = await SportRepository().get_one(record_id=tournament.sport_id)

    res = GetTournamentPageSchema(
        **tournament_dict,
        admin=BriefUserSchema(**admin.__dict__),
        players_count=len(tournament.players_id),
        sport_title=sport.name
    )

    return res


@tournament_router.get("/{id}/players", response_model=List[BriefUserSchema])
async def get_players(id: uuid.UUID) -> List[BriefUserSchema]:
    """Получить игроков турнира"""
    tournament = await TournamentRepository().get_one(record_id=id)
    data = await UserRepository().get_many(tournament.players_id)
    users = sorted((BriefUserSchema(**user.__dict__) for user in data), key=lambda p: p.full_name)
    return users


@tournament_router.patch("/{id}")
async def patch_tournament(id: uuid.UUID, tournament: PatchTournamentSchema):
    """Редактирование турнира"""
    tournament_repo = TournamentRepository()
    sport_repo = SportRepository()

    current_tournament = await tournament_repo.get_one(record_id=id)
    if not current_tournament:
        raise HTTPException(status_code=400, detail="The tournament with the transferred ID does not exist.")

    if tournament.sport_id and not await sport_repo.find_one(record_id=tournament.sport_id):
        raise HTTPException(status_code=400, detail="The sport with the transferred ID does not exist.")

    if tournament.enroll_start_time or tournament.enroll_end_time or tournament.start_time:
        enroll_start_time = tournament.enroll_start_time or current_tournament.enroll_start_time
        enroll_end_time = tournament.enroll_end_time or current_tournament.enroll_end_time
        start_time = tournament.start_time or current_tournament.start_time

        if not enroll_start_time < enroll_end_time <= start_time:
            raise HTTPException(status_code=400, detail="Incorrect time frame of the tournament is specified.")

    update_data = tournament.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_tournament, key, value)

    updated_tournament_data = {key: getattr(current_tournament, key) for key in update_data.keys()}

    await tournament_repo.update_one(record_id=id, data=updated_tournament_data)
    result = await tournament_repo.get_one(record_id=id)
    return result
