import uuid

from grid_generator.models.schemas import PlayerResultSchema, ResultsSchema, GridUserSchema
from grid_generator.repository import MatchRepository


async def get_next_match(grid_match_number: int, round_number: int, main_rounds_count: int) -> int:
    players_count = 1 << main_rounds_count
    round_match_count = players_count >> round_number
    round_match_number = grid_match_number % (round_match_count << 1)
    max_round_match_number = grid_match_number + round_match_count - round_match_number
    next_match_number = max_round_match_number + ((round_match_number + 1) >> 1)
    return next_match_number


async def update_next_match(grid_match_number: int,
                            next_match_number: int,
                            round_number: int,
                            rounds: list,
                            winner_id: uuid.UUID):
    next_match = (await MatchRepository().find_all({
        "round_id": rounds[round_number].id,
        "grid_match_number": next_match_number
    }, AND=True))[0]
    players_id = next_match.players_id
    players_id[grid_match_number & 1 ^ 1] = winner_id
    await MatchRepository().update_one(record_id=next_match.id, data={"players_id": players_id})


async def get_update_winner(_match, match_id: uuid.UUID) -> uuid.UUID:
    winner_id = _match.players_id[max(0, 1, key=lambda i: _match.score[i])]
    await MatchRepository().update_one(record_id=match_id, data={"winner_id": winner_id})
    return winner_id


def get_results_object(player, place) -> PlayerResultSchema:
    return PlayerResultSchema(
        player=player,
        place=place
    )


async def get_match_results(_match, players, loser_place, winner_place=None) -> PlayerResultSchema | list[PlayerResultSchema]:
    loser_id = list(set(_match.players_id) - {_match.winner_id})[0]
    winner_id = _match.winner_id
    loser = get_results_object(players[loser_id], loser_place)
    winner = get_results_object(players[winner_id], winner_place) if winner_place else None
    return loser if not winner_place else [loser, winner]
