import uuid

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
