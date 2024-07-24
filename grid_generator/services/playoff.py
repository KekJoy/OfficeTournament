import uuid

from math import log2

from grid_generator.repository import RoundRepository, MatchRepository
from grid_generator.services.results import get_match_results


class PlayoffCreator:
    def __init__(self, shuffled_players: list[uuid.UUID], grid_id: uuid.UUID):
        self.players = shuffled_players
        self.grid_id = grid_id
        self.rounds_count = log2(len(shuffled_players))
        self.matches = []
        self.current_match_number = 1

    async def create(self) -> list:
        for round_number in range(1, int(self.rounds_count)+1):
            round_id = await RoundRepository().add_round(round_number=round_number, grid_id=self.grid_id)
            await self.add_round_matches(round_number, round_id)
        return self.matches

    async def add_round_matches(self, round_number: int, round_id: uuid.UUID) -> None:
        if round_number == 1:
            return await self.add_first_round_matches(round_id)
        await self.add_other_round_matches(round_id, round_number)

    async def add_first_round_matches(self, round_id: uuid.UUID) -> None:
        for j in range(len(self.players) // 2):
            players = [self.players[j * 2], self.players[j * 2 + 1]]
            _match = await MatchRepository().add_round_match(
                round_id=round_id,
                number=self.current_match_number,
                players=players)
            self.current_match_number += 1
            self.matches.append(_match)

    async def add_other_round_matches(self, round_id: uuid.UUID, round_number: int) -> None:
        for j in range(int(2 ** (self.rounds_count - round_number))):
            _match = await MatchRepository().add_round_match(round_id=round_id, number=self.current_match_number)
            self.current_match_number += 1
            self.matches.append(_match)


async def create_playoff(players: list[uuid.UUID], grid_id: uuid.UUID):
    return await PlayoffCreator(players, grid_id).create()


async def get_playoff_results(grid, rounds, players):
    worst = len(players.keys())
    res = []
    for _round in rounds:
        if _round.round_number == 0:
            continue

        matches = await MatchRepository().find_all(conditions={'round_id': _round.id})
        best = worst - len(matches) + 1
        range_place = f"{best} — {worst}"
        worst -= len(matches)

        if best == 2:
            res += await get_match_results(matches[0], players, "2", "1")
        elif best == 3 and grid.third_place_match:
            _match = rounds[0]
            res += await get_match_results(_match, players, "4", "3")
        else:
            res += [await get_match_results(_match, players, range_place) for _match in matches]
    return res
