from http.client import HTTPException

from tournaments.repository import GridRepository
from tournaments.models.utils import GridTypeENUM
from .queue import shuffle_players

from .playoff import create_playoff
from .circle import create_circle


async def get_matches_by_grid_type(players, grid):
    if grid.grid_type == GridTypeENUM.PLAYOFF:
        return await create_playoff(players, grid.id)
    elif grid.grid_type == GridTypeENUM.CIRCLE:
        return await create_circle(players, grid.id)
    else:
        raise HTTPException(status_code=400, detail="Wrong grid type")


async def start(tournament: dict) -> None:
    players = tournament["players_id"]
    grid = await GridRepository().get_one(tournament["grid"])
    players = await shuffle_players(players, grid.id)
    await get_matches_by_grid_type(players, grid)
