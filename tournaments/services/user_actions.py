import uuid

from fastapi import HTTPException

from auth.repository import UserRepository
from tournaments.models.schemas import GetTournamentSchema
from tournaments.repository import TournamentRepository
from tournaments.services.tournament import tournament_router


@tournament_router.post("/{id}/enroll/{user_id}")
async def user_enroll(id: uuid.UUID, user_id: uuid.UUID) -> GetTournamentSchema:
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
