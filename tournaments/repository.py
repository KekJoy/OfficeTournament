from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from database import async_session_maker
from utils.repository import SQLALchemyRepository
from tournaments.models.db import Tournament, Sport, Grid


class TournamentRepository(SQLALchemyRepository):
    model = Tournament

    async def get_multiple(self, skip, limit):
        async with async_session_maker() as session:
            try:
                query = select(self.model).offset(skip).limit(limit)
                result = await session.execute(query)
                return result.scalars().all()
            except NoResultFound:
                return []


class SportRepository(SQLALchemyRepository):
    model = Sport


class GridRepository(SQLALchemyRepository):
    model = Grid

