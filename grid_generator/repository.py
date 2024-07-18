from utils.repository import SQLALchemyRepository
from grid_generator.models.db import Round, Match, Game


class RoundRepository(SQLALchemyRepository):
    model = Round


class MatchRepository(SQLALchemyRepository):
    model = Match


class GameRepository(SQLALchemyRepository):
    model = Game
