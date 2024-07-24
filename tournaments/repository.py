import uuid

from sqlalchemy import select, func, and_, cast, Date, any_, text
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

    async def filter_tournaments(self, filters: dict):
        async with async_session_maker() as session:
            query = select(self.model)
            conditions = []

            if 'sport_id' in filters and filters['sport_id'] is not None:
                conditions.append(self.model.sport_id == filters['sport_id'])

            if 'start_time_from' in filters and filters['start_time_from'] is not None:
                conditions.append(cast(self.model.start_time, Date) >= filters['start_time_from'])

            if 'start_time_to' in filters and filters['start_time_to'] is not None:
                conditions.append(cast(self.model.start_time, Date) <= filters['start_time_to'])

            if 'status' in filters and filters['status'] is not None:
                conditions.append(self.model.status.in_(filters['status']))

            if 'is_solo' in filters:
                if filters['is_solo'] is True:
                    conditions.append(self.model.team_players_limit == 1)
                elif filters['is_solo'] is False:
                    conditions.append(self.model.team_players_limit > 1)

            if conditions:
                query = query.where(and_(*conditions))

            result = await session.execute(query)
            tournaments = result.scalars().all()
            return tournaments

    async def find_user_tournaments(self, user_id: uuid.UUID, filters: dict = None):
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.players_id.any(user_id))
            conditions = [self.model.players_id.any(user_id)]

            if filters:
                if 'sport_id' in filters and filters['sport_id'] is not None:
                    conditions.append(self.model.sport_id == filters['sport_id'])

                if 'start_time_from' in filters and filters['start_time_from'] is not None:
                    conditions.append(cast(self.model.start_time, Date) >= filters['start_time_from'])

                if 'start_time_to' in filters and filters['start_time_to'] is not None:
                    conditions.append(cast(self.model.start_time, Date) <= filters['start_time_to'])

                if 'status' in filters and filters['status'] is not None:
                    conditions.append(self.model.status.in_(filters['status']))

                if 'is_solo' in filters:
                    if filters['is_solo'] is True:
                        conditions.append(self.model.team_players_limit == 1)
                    elif filters['is_solo'] is False:
                        conditions.append(self.model.team_players_limit > 1)

            if conditions:
                query = query.where(and_(*conditions))

            result = await session.execute(query)
            tournaments = result.scalars().all()
            return tournaments


class SportRepository(SQLALchemyRepository):
    model = Sport


class GridRepository(SQLALchemyRepository):
    model = Grid
