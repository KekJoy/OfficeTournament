import uuid
from typing import Annotated

from fastapi import HTTPException, Depends, Header, APIRouter

from auth.jwt_checker import check_jwt
from auth.models.db import User
from auth.repository import UserRepository
from tournaments.models.schemas import GetTournamentSchema
from tournaments.repository import TournamentRepository, GridRepository

user_actions = APIRouter(prefix="/user-actions", tags=["User Actions"])


@user_actions.post("/{id}/enroll")
async def user_enroll(id: uuid.UUID, user: User = Depends(check_jwt),
                      Authorization: Annotated[list[str] | None, Header()] = None) -> GetTournamentSchema:
    """Участвовать в турнире"""
    # TODO: check authorization
    tournament = await TournamentRepository().get_one(record_id=id)
    grid_type = await GridRepository().get_one(record_id=tournament.grid)
    players_id = tournament.players_id or []
    if user.id in players_id:
        raise HTTPException(status_code=400, detail="The user is already enrolled.")
    if len(players_id) >= tournament.teams_limit:
        raise HTTPException(status_code=400, detail="The players limit has been reached.")
    if not await UserRepository().find_one(record_id=user.id):
        raise HTTPException(status_code=400, detail="User doesn't exist.")
    players_id.append(user.id)
    await TournamentRepository().update_one(record_id=id, data={"players_id": players_id})
    tournament_dict = tournament.__dict__
    tournament_dict['grid_type'] = grid_type.grid_type
    return GetTournamentSchema(**tournament_dict)


@user_actions.post("/{id}/unenroll")
async def user_unenroll(id: uuid.UUID, user: User = Depends(check_jwt),
                        Authorization: Annotated[list[str] | None, Header()] = None) -> GetTournamentSchema:
    """Выйти из турнира"""
    tournament = await TournamentRepository().get_one(record_id=id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found.")

    players_id = tournament.players_id or []

    if user.id not in players_id:
        raise HTTPException(status_code=400, detail="The user is not enrolled in the tournament.")

    players_id.remove(user.id)
    await TournamentRepository().update_one(record_id=id, data={"players_id": players_id})

    grid_type = await GridRepository().get_one(record_id=tournament.grid)
    tournament_dict = tournament.__dict__
    tournament_dict['grid_type'] = grid_type.grid_type

    return GetTournamentSchema(**tournament_dict)
