import uuid

from fastapi import APIRouter, HTTPException, Query

from auth.repository import UserRepository
from grid_generator.repository import RoundRepository, MatchRepository, GameRepository
from grid_generator.models.schemas import RoundSchema, BasicMatchSchema, GridSchema, GridSchemaWrapped, GridUserSchema, \
    MatchSchema, WrappedMatchSchema, GameSchema, UpdateScoreSchema
from tournaments.repository import TournamentRepository, GridRepository
from .util import get_users_dict, to_dict_list


grid_router = APIRouter(prefix='/grid', tags=['grids'])


@grid_router.get('/{tournament_id}')
async def get_grid(tournament_id: uuid.UUID) -> GridSchemaWrapped:
    """Get grid data"""
    tournament = await TournamentRepository().get_one(record_id=tournament_id)
    grid_id = tournament.grid
    _grid = await GridRepository().get_one(record_id=grid_id)
    users = await get_users_dict(tournament.players_id)

    rounds = to_dict_list(await RoundRepository().find_all(conditions={'grid_id': grid_id}))

    for _round in rounds:
        matches = to_dict_list(await MatchRepository().find_all(conditions={'round_id': _round["id"]}))
        matches.sort(key=lambda m: m["grid_match_number"])
        for m in matches:
            m['players'] = [users.get(p) for p in m['players_id']]
        _round['matches'] = [BasicMatchSchema(**m) for m in matches]

    rounds = [RoundSchema(**r) for r in rounds]
    wrapped = GridSchemaWrapped(grid=GridSchema(id=grid_id, grid_type=_grid.grid_type, rounds=rounds, third_place_match=None))
    return wrapped


@grid_router.get('/match/{id}')
async def get_match(id: uuid.UUID) -> WrappedMatchSchema:
    """Get all match data"""
    _match = await MatchRepository().get_one(record_id=id)
    _round = await RoundRepository().get_one(record_id=_match.round_id)

    _games = await GameRepository().find_all(conditions={'match_id': _match.id}) or []

    _players = await get_users_dict(_match.players_id)
    players = list(_players.values())

    games = []
    for i in _games:
        games.append(GameSchema(**i.__dict__))
    for i in range(len(_games) + 1, _round.game_count + 1):
        game_id = await GameRepository().add_match_game(_match.id, i)
        game = await GameRepository().get_one(record_id=game_id)
        games.append(GameSchema(**game.__dict__))

    base = BasicMatchSchema(**_match.__dict__, players=players)
    res = MatchSchema(**base.__dict__, games=games)

    return WrappedMatchSchema(match=res)


@grid_router.patch("/match/{id}")
async def update_match(id: uuid.UUID, match_score: UpdateScoreSchema) -> UpdateScoreSchema:
    """Update match score"""
    await MatchRepository().update_one(record_id=id, data={"score": match_score.score})
    return match_score


@grid_router.patch("/game/{id}")
async def update_game(id: uuid.UUID, game_score: UpdateScoreSchema) -> UpdateScoreSchema:
    """Update game score"""
    await GameRepository().update_one(record_id=id, data={"score": game_score.score})
    return game_score


@grid_router.get("/match/{id}/end")
async def end_match(id: uuid.UUID) -> uuid.UUID:
    # TODO: implement CIRCLE grid type
    """End match, move winner on"""
    _match = await MatchRepository().get_one(record_id=id)
    _round = await RoundRepository().get_one(record_id=_match.round_id)
    rounds = await RoundRepository().find_all(conditions={'grid_id': _round.grid_id})

    main_rounds_count = max(rounds, key=lambda r: r.round_number).round_number

    if _round.round_number == main_rounds_count:
        winner_id = _match.players_id[max(0, 1, key=lambda i: _match.score[i])]
        await MatchRepository().update_one(record_id=id, data={"winner_id": winner_id})
        return winner_id

    main_rounds_count = 3
    round_number = _round.round_number

    players_count = 1 << main_rounds_count
    round_match_count = players_count >> round_number
    round_match_number = _match.grid_match_number % (round_match_count << 1)
    max_round_match_number = _match.grid_match_number + round_match_count - round_match_number
    next_match_number = max_round_match_number + ((round_match_number + 1) >> 1)

    winner_id = _match.players_id[max(0, 1, key=lambda i: _match.score[i])]
    await MatchRepository().update_one(record_id=id, data={"winner_id": winner_id})

    next_match = (await MatchRepository().find_all({
        "round_id": rounds[_round.round_number].id,
        "grid_match_number": next_match_number
    }, AND=True))[0]
    players_id = next_match.players_id
    players_id[_match.grid_match_number & 1 ^ 1] = winner_id
    await MatchRepository().update_one(record_id=next_match.id, data={"players_id": players_id})
    return winner_id

@grid_router.get("/results/{tournament_id}")
async def get_results(tournament_id: uuid.UUID):
    tournament = await TournamentRepository().get_one(record_id=tournament_id)
    grid_id = tournament.grid
    players_id = tournament.players_id
    grid = await GridRepository().get_one(record_id=grid_id)

    worst = len(players_id)
    res = []

    rounds = await RoundRepository().find_all(conditions={'grid_id': grid_id})
    for _round in rounds:
        matches = await MatchRepository().find_all(conditions={'round_id': _round.id})
        best = worst - len(matches) + 1
        for _match in matches:
            loser = list(set(_match.players_id) - {_match.winner_id})[0]
            res.append({
                "player_id": loser,
                "place": f"{worst} - {best}"
            })
            worst -= 1

    return res
