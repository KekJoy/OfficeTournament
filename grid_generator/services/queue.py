import uuid

import random
from utils.dict import get_users_dict

from tournaments.repository import TournamentRepository, GridRepository
from .grid import grid_router
from grid_generator.repository import RoundRepository, MatchRepository
from ..models.schemas import QueueSchema, BasicMatchSchema


async def shuffle_players(players_id: list[uuid.UUID], grid_id: uuid.UUID) -> list[uuid.UUID]:
    rd = random.Random(int(grid_id))
    new_players = players_id[:]
    rd.shuffle(new_players)
    return new_players


@grid_router.get("/{tournament_id}/queue")
async def get_queue(tournament_id: uuid.UUID) -> QueueSchema:
    tournament = await TournamentRepository().get(record_id=tournament_id)
    players = await get_users_dict(tournament.players_id)
    grid = await GridRepository().get(record_id=tournament.grid)
    rounds = await RoundRepository().find_all(conditions={"grid_id": grid.id})
    res = [None] * 50

    for _round in rounds:
        matches = await MatchRepository().find_all(conditions={"round_id": _round.id})
        for _match in matches:
            match_dict = _match.__dict__
            match_dict["players"] = [players.get(_id) for _id in match_dict["players_id"]]
            res[match_dict["queue_match_number"]] = BasicMatchSchema(**match_dict)
    return QueueSchema(matches=[x for x in res if x])
