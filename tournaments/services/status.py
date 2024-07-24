import uuid

from fastapi import HTTPException

from tournaments.models.utils import TournamentStatusENUM as TS
from tournaments.repository import TournamentRepository
from .tournament import tournament_router


async def set_tournament_status(id: uuid.UUID, status: TS, allowed_statuses: set[TS] | None = None, msg=""):
    tournament = await TournamentRepository().get(record_id=id)
    if allowed_statuses and tournament.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=msg)
    await TournamentRepository().update_one(record_id=id, data={"status": status})


@tournament_router.post("/{id}/open-enroll")
async def open_enroll(id: uuid.UUID):
    await set_tournament_status(id,
                                TS.REGISTRATION_OPEN,
                                {TS.SCHEDULED, TS.REGISTRATION_CLOSE},
                                "Cannot open enrollment")
    return "ok"


@tournament_router.post("/{id}/close-enroll")
async def close_enroll(id: uuid.UUID):
    await set_tournament_status(id,
                                TS.REGISTRATION_CLOSE,
                                {TS.REGISTRATION_OPEN},
                                "Cannot close enrollment")
    return "ok"


@tournament_router.post("/{id}/cancel")
async def cancel(id: uuid.UUID):
    await set_tournament_status(id, TS.CANCELED, None)
    return "ok"
