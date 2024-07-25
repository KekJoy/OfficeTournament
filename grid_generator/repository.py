import uuid

from config import app_settings

from utils.repository import SQLALchemyRepository
from grid_generator.models.db import Round, Match, Game


class RoundRepository(SQLALchemyRepository):
    model = Round

    def add_round(self, round_number: int, grid_id: uuid.UUID):
        return self.add_one(data={
            "round_number": round_number,
            "game_count": app_settings.DEFAULT_GAME_COUNT,
            "grid_id": grid_id})


class MatchRepository(SQLALchemyRepository):
    model = Match

    def add_round_match(self, round_id, grid_number=0, queue_number=0, players=None):
        players = players or [None, None]
        return self.add_one(data={
            "grid_match_number": grid_number,
            "queue_match_number": queue_number,
            "round_id": round_id,
            "players_id": players,
            "score": [0, 0]
        })


class GameRepository(SQLALchemyRepository):
    model = Game

    def add_match_game(self, match_id: uuid.UUID, game_number: int):
        return self.add_one(data={
            "match_id": match_id,
            "score": [0, 0],
            "game_number": game_number
        })
