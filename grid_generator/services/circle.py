import uuid

from grid_generator.models.schemas import PlayerResultSchema
from grid_generator.repository import RoundRepository, MatchRepository


async def create_circle(shuffled_players: list[uuid.UUID], grid_id: uuid.UUID) -> list:
    players_count = len(shuffled_players)
    round_id = await RoundRepository().add_round(round_number=1, grid_id=grid_id)
    current_match_number = 1
    matches = []
    for i in range(players_count - 1):
        for j in range(i + 1, players_count):
            match_players = [shuffled_players[i], shuffled_players[j]]
            _match = await MatchRepository().add_round_match(
                round_id=round_id,
                number=current_match_number,
                players=match_players)
            matches.append(_match)
            current_match_number += 1
    return matches


async def compute_match(_match, scores):
    players_id = _match.players_id
    score = _match.score
    if score[0] == score[1]:
        await add_both(scores, players_id)
    else:
        await add_winner(scores, players_id, score)


async def add_both(scores, players_id):
    for player_id in players_id:
        scores[player_id] += 1


async def add_winner(scores, players_id, score):
    winner_id = [players_id[i] for i in [0, 1] if score[i] == max(score)][0]
    scores[winner_id] += 3


async def get_circle_results(_round, players: dict):
    matches = await MatchRepository().find_all(conditions={"round_id": _round.id})

    scores = {p: 0 for p in players.keys()}

    for _match in matches:
        await compute_match(_match, scores)

    res = []

    players_scores = sorted(scores.items(), key=lambda ps: ps[1])

    for i, ps in enumerate(players_scores[::-1]):
        res.append(PlayerResultSchema(player=players[ps[0]], place=str(i + 1)))

    return res
