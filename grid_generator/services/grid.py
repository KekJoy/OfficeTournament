import uuid

from fastapi import APIRouter, HTTPException, Depends, Header

from auth.jwt_checker import check_jwt
from auth.models.db import User
from grid_generator.repository import RoundRepository, MatchRepository, GameRepository
from grid_generator.models.schemas import RoundSchema, BasicMatchSchema, GridSchema, GridSchemaWrapped, MatchSchema, \
    WrappedMatchSchema, GameSchema, UpdateScoreSchema, SetGameCountSchema, ResultsSchema
from grid_generator.services.results import get_next_match, update_next_match, get_update_winner
from tournaments.models.schemas import BriefUserSchema
from tournaments.models.utils import TournamentStatusENUM, GridTypeENUM
from tournaments.repository import TournamentRepository, GridRepository
from utils.dict import get_users_dict, to_dict_list
from .playoff import get_playoff_results
from .circle import get_circle_results


grid_router = APIRouter(prefix='/grid', tags=['Grids'])


@grid_router.get('/{tournament_id}')
async def get_grid(tournament_id: uuid.UUID,
                   user: User = Depends(check_jwt), Authorization: str = Header()) -> GridSchemaWrapped:
    """Get grid data"""
    tournament = await TournamentRepository().get(record_id=tournament_id)
    if tournament.status != TournamentStatusENUM.PROGRESS:
        raise HTTPException(status_code=400, detail='The tournament has not begun yet')
    grid_id = tournament.grid
    _grid = await GridRepository().get(record_id=grid_id)
    users = await get_users_dict(tournament.players_id)

    rounds = to_dict_list(await RoundRepository().find_all(conditions={'grid_id': grid_id}))

    for _round in rounds:
        matches = to_dict_list(await MatchRepository().find_all(conditions={'round_id': _round["id"]}))
        matches.sort(key=lambda m: m["grid_match_number"])
        for m in matches:
            m['players'] = [users.get(p) for p in m['players_id']]
        _round['matches'] = [BasicMatchSchema(**m) for m in matches]

    rounds = [RoundSchema(**r) for r in rounds]
    wrapped = GridSchemaWrapped(
        grid=GridSchema(id=grid_id, grid_type=_grid.grid_type, rounds=rounds, third_place_match=None))
    return wrapped


@grid_router.get('/match/{id}')
async def get_match(id: uuid.UUID,
                    user: User = Depends(check_jwt), Authorization: str = Header()) -> WrappedMatchSchema:
    """Get all match data"""
    _match = await MatchRepository().get(record_id=id)
    _round = await RoundRepository().get(record_id=_match.round_id)

    _games = await GameRepository().find_all(conditions={'match_id': _match.id}) or []

    _players = await get_users_dict(_match.players_id)
    players = [_players.get(p) for p in _match.players_id]

    games = []
    for i in _games:
        games.append(GameSchema(**i.__dict__))
    for i in range(len(_games) + 1, _round.game_count + 1):
        game_id = await GameRepository().add_match_game(_match.id, i)
        game = await GameRepository().get(record_id=game_id)
        games.append(GameSchema(**game.__dict__))

    base = BasicMatchSchema(**_match.__dict__, players=players)
    res = MatchSchema(**base.__dict__, games=sorted(games, key=lambda g: g.id))

    return WrappedMatchSchema(match=res)


@grid_router.patch("/match/{id}")
async def update_match(id: uuid.UUID, match_score: UpdateScoreSchema,
                       user: User = Depends(check_jwt), Authorization: str = Header()) -> UpdateScoreSchema:
    """Update match score"""
    _match = await MatchRepository().get(record_id=id)
    if not _match:
        raise HTTPException(status_code=404, detail="The match doesn't exist.")
    if not all(_match.players_id):
        raise HTTPException(status_code=400, detail="The match is not valid yet.")
    await MatchRepository().update_one(record_id=id, data={"score": match_score.score})
    return match_score


@grid_router.patch("/game/{id}")
async def update_game(id: uuid.UUID, game_score: UpdateScoreSchema,
                      user: User = Depends(check_jwt), Authorization: str = Header()) -> UpdateScoreSchema:
    """Update game score"""
    game = await GameRepository().get(record_id=id)
    if not game:
        raise HTTPException(status_code=404, detail="The game doesn't exist.")
    await GameRepository().update_one(record_id=id, data={"score": game_score.score})
    return game_score


@grid_router.get("/match/{id}/end")
async def end_match(id: uuid.UUID,
                    user: User = Depends(check_jwt), Authorization: str = Header()) -> uuid.UUID:
    """End match, move winner on"""
    _match = await MatchRepository().get(record_id=id)
    _round = await RoundRepository().get(record_id=_match.round_id)
    rounds = await RoundRepository().find_all(conditions={'grid_id': _round.grid_id})

    main_rounds_count = max(rounds, key=lambda r: r.round_number).round_number
    grid_match_number = _match.grid_match_number
    round_number = _round.round_number

    if not _round or not _match:
        raise HTTPException(status_code=404, detail="The round or the match doesn't exist")
    if not all(_match.players_id):
        raise HTTPException(status_code=400, detail="The match is not valid yet.")

    if round_number == main_rounds_count:
        return await get_update_winner(_match, id)

    next_match_number = await get_next_match(
        grid_match_number,
        round_number,
        main_rounds_count)

    winner_id = await get_update_winner(_match, id)

    await update_next_match(grid_match_number, next_match_number, round_number, rounds, winner_id)
    return winner_id


@grid_router.get("/{tournament_id}/results")
async def get_results(tournament_id: uuid.UUID
                      ) -> ResultsSchema:
    tournament = await TournamentRepository().get(record_id=tournament_id)

    grid_id = tournament.grid
    grid = await GridRepository().get(record_id=grid_id)
    players = await get_users_dict(tournament.players_id, BriefUserSchema)

    rounds = sorted(await RoundRepository().find_all(conditions={'grid_id': grid.id}), key=lambda r: r.round_number)

    res = await get_playoff_results(grid, rounds, players) if grid.grid_type == GridTypeENUM.PLAYOFF\
        else await get_circle_results(rounds[0], players)

    return ResultsSchema(results=res)


@grid_router.patch("/round/{round_id}/set_game_count")
async def set_game_count(round_id: uuid.UUID, game_count: SetGameCountSchema,
                         user: User = Depends(check_jwt), Authorization: str = Header()):
    _round = await RoundRepository().get(record_id=round_id)
    if not _round:
        raise HTTPException(status_code=400, detail="Round doesn't exist.")
    await RoundRepository.update_one(record_id=round_id, data={"game_count": game_count.game_count})
    return "ok"

