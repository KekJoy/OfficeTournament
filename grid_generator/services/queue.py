import uuid

import random


async def shuffle_players(players_id: list[uuid.UUID], grid_id: uuid.UUID) -> list[uuid.UUID]:
    rd = random.Random(int(grid_id))
    new_players = players_id[:]
    rd.shuffle(new_players)
    return new_players
