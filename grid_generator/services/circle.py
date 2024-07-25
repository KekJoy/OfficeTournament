import uuid

from grid_generator.models.schemas import PlayerResultSchema
from grid_generator.repository import RoundRepository, MatchRepository


async def get_circle_order(player_count: int) -> list[tuple[int, int]]:
    order = [(0, 0)]

    for group_size in range(2, player_count // 2 + 2):
        group_pairs = 0

        first = 0
        while group_pairs < player_count:
            if player_count & 1 == 0 and group_pairs == player_count // 2 and group_size == player_count // 2 + 1:
                break
            second = (first + group_size - 1) % player_count
            while first in order[-1] or second in order[-1] or (first, second) in order:
                first = (first + 1) % player_count
                second = (second + 1) % player_count
                if group_size == player_count // 2 or player_count <= 4:
                    break
            order.append(tuple(sorted((first, second))))
            group_pairs += 1
            first = (second + 1) % player_count
    return order[1:]


async def get_queue_number_dict(order: list[tuple[int, int]]) -> dict[tuple[int, int], int]:
    return {v: k for k, v in enumerate(order)}


async def create_circle(shuffled_players: list[uuid.UUID], grid_id: uuid.UUID) -> list:
    players_count = len(shuffled_players)
    round_id = await RoundRepository().add_round(round_number=1, grid_id=grid_id)
    current_match_number = 1
    matches = []
    match_queue_order = await get_circle_order(players_count)
    get_queue_number = await get_queue_number_dict(match_queue_order)
    for i in range(players_count - 1):
        for j in range(i + 1, players_count):
            match_players = [shuffled_players[i], shuffled_players[j]]
            _match = await MatchRepository().add_round_match(
                round_id=round_id,
                grid_number=current_match_number,
                queue_number=get_queue_number[(i, j)],
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
