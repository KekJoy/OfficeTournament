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

    def add_round_match(self, round_id, number=0, players=None):
        players = players or []
        return self.add_one(data={
            "grid_match_number": number,
            "queue_match_number": number,
            "round_id": round_id,
            "players_id": players,
            "score": []
        })


class GameRepository(SQLALchemyRepository):
    model = Game
