import uuid

from fastapi import HTTPException, Depends, Header

from auth.jwt_checker import check_jwt
from auth.models.db import User
from tournaments.models.utils import TournamentStatusENUM as TS
from tournaments.repository import TournamentRepository
from .tournament import tournament_router


async def set_tournament_status(id: uuid.UUID, user: User, status: TS, allowed_statuses: set[TS] | None = None, msg=""):
    tournament = await TournamentRepository().get(record_id=id)
    # if user not in tournament.admins_id:
    #     raise HTTPException(status_code=403, detail="You cannot change the tournament status")
    if allowed_statuses and tournament.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=msg)
    await TournamentRepository().update_one(record_id=id, data={"status": status})


@tournament_router.patch("/{id}/open-enroll")
async def open_enroll(id: uuid.UUID, user: User = Depends(check_jwt), Authorization: str = Header()):
    await set_tournament_status(id,
                                user,
                                TS.REGISTRATION_OPEN,
                                {TS.SCHEDULED, TS.REGISTRATION_CLOSE},
                                "Cannot open enrollment")
    return "ok"


@tournament_router.patch("/{id}/close-enroll")
async def close_enroll(id: uuid.UUID, user: User = Depends(check_jwt), Authorization: str = Header()):
    await set_tournament_status(id,
                                user,
                                TS.REGISTRATION_CLOSE,
                                {TS.REGISTRATION_OPEN},
                                "Cannot close enrollment")
    return "ok"


@tournament_router.patch("/{id}/cancel")
async def cancel(id: uuid.UUID, user: User = Depends(check_jwt), Authorization: str = Header()):
    await set_tournament_status(id, user, TS.CANCELED, None)
    return "ok"


@tournament_router.patch("/id/end")
async def end(id: uuid.UUID, user: User = Depends(check_jwt), Authorization: str = Header()):
    await set_tournament_status(id, user, TS.COMPLETED, {TS.PROGRESS}, msg="Cannot end the tournament")
    return "ok"
