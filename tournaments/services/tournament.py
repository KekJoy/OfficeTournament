import uuid
from typing import List, Dict, Annotated

from fastapi import APIRouter, HTTPException, Query, Depends, Header

from auth.jwt_checker import check_jwt
from auth.models.db import User
from auth.repository import UserRepository
from tournaments.models.schemas import CreateTournamentSchema, TournamentFiltersSchema, \
    GetTournamentPageSchema, BriefUserSchema, TournamentResponse, PatchTournamentSchema, \
    GetTournamentSchemaWithSportTitle
from tournaments.repository import SportRepository, TournamentRepository, GridRepository
from tournaments.models.utils import TournamentStatusENUM
from utils.dict import get_id_dict
from grid_generator.services.start import start

tournament_router = APIRouter(prefix='/tournament', tags=['Tournaments'])


@tournament_router.post("/create", response_model=uuid.UUID)
async def create_tournament(tournament: CreateTournamentSchema,
                            user: User = Depends(check_jwt), Authorization: str = Header()) -> uuid.UUID:
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
    grid_id = await GridRepository().add_one({
        "grid_type": f"{tournament.grid_type}",
        "third_place_match": tournament.third_place_match
    })
    tournament_dict = tournament.model_dump()
    del tournament_dict["grid_type"]
    del tournament_dict["third_place_match"]
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

    sports_list = await SportRepository().get([t.sport_id for t in tournaments])
    sports = get_id_dict(sports_list)

    result = []
    for trnmt in tournaments:
        grid = await GridRepository().get(trnmt.grid)
        grid_type = grid.grid_type if grid else None

        tournament_dict = trnmt.__dict__
        tournament_dict['grid_type'] = grid_type
        tournament_dict['sport_title'] = sports[trnmt.sport_id].name
        del tournament_dict['grid']
        result.append(GetTournamentSchemaWithSportTitle(**tournament_dict))

    total_count = len(result)
    return TournamentResponse(total_count=total_count, tournaments=result[offset_min:offset_max])


@tournament_router.get("/{id}", response_model=GetTournamentPageSchema)
async def get_tournament(id: uuid.UUID) -> GetTournamentPageSchema:
    """Получить турнир по ID"""
    tournament = await TournamentRepository().get(record_id=id)
    if not tournament:
        raise HTTPException(status_code=400, detail="The tournament with the transferred ID does not exist.")
    grid = await GridRepository().get(tournament.grid)
    grid_type = grid.grid_type if grid else None

    tournament_dict = tournament.__dict__
    tournament_dict['grid_type'] = grid_type
    del tournament_dict['grid']

    admin = await UserRepository().get(record_id=tournament.admins_id[0])
    sport = await SportRepository().get(record_id=tournament.sport_id)

    res = GetTournamentPageSchema(
        **tournament_dict,
        admin=BriefUserSchema(**admin.__dict__),
        players_count=len(tournament.players_id) if tournament.players_id else 0,
        sport_title=sport.name
    )

    return res


@tournament_router.get("/{id}/players", response_model=List[BriefUserSchema])
async def get_players(id: uuid.UUID, user: User = Depends(check_jwt), Authorization: str = Header()) -> List[BriefUserSchema]:
    """Получить игроков турнира"""
    tournament = await TournamentRepository().get(record_id=id)
    data = await UserRepository().get(tournament.players_id)
    users = sorted((BriefUserSchema(**user.__dict__) for user in data), key=lambda p: p.full_name)
    return users


@tournament_router.get("/{id}/start")
async def start_tournament(id: uuid.UUID, user: User = Depends(check_jwt), Authorization: str = Header()) -> None:
    """Начинает турнир"""
    tournament = await TournamentRepository().get(record_id=id)
    if tournament.admins_id[0] != user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of the tournament.")
    await TournamentRepository().update_one(record_id=id, data={"status": TournamentStatusENUM.PROGRESS})
    await start(tournament.__dict__)


@tournament_router.patch("/{id}")
async def patch_tournament(id: uuid.UUID, tournament: PatchTournamentSchema,
                           user: User = Depends(check_jwt), Authorization: str = Header()):
    """Редактирование турнира"""

    tournament_repo = TournamentRepository()
    sport_repo = SportRepository()

    current_tournament = await tournament_repo.get(record_id=id)
    if not current_tournament:
        raise HTTPException(status_code=400, detail="The tournament with the transferred ID does not exist.")

    if current_tournament.admins_id[0] != user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of the tournament.")

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
    result = await tournament_repo.get(record_id=id)
    return result


@tournament_router.post("/user_tournaments", response_model=TournamentResponse)
async def get_user_tournaments(user: User = Depends(check_jwt),
                               Authorization: Annotated[list[str] | None, Header()] = None,
                               page: int = Query(ge=1, default=1),
                               size: int = Query(ge=1, le=100)) -> TournamentResponse:
    """Получить турниры, в которых участвует пользователь"""
    offset_min = (page - 1) * size
    offset_max = page * size

    tournaments = await TournamentRepository().find_user_tournaments(user.id)

    sports_list = await SportRepository().get([t.sport_id for t in tournaments])
    sports = get_id_dict(sports_list)

    result = []
    for trnmt in tournaments:
        grid = await GridRepository().get(trnmt.grid)
        grid_type = grid.grid_type if grid else None

        tournament_dict = trnmt.__dict__
        tournament_dict['grid_type'] = grid_type
        tournament_dict['sport_title'] = sports[trnmt.sport_id].name
        del tournament_dict['grid']
        result.append(GetTournamentSchemaWithSportTitle(**tournament_dict))

    total_count = len(result)
    return TournamentResponse(total_count=total_count, tournaments=result[offset_min:offset_max])
