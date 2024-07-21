import uuid

from auth.models.db import User
from utils.repository import SQLALchemyRepository
from sqlalchemy import select

from database import async_session_maker


class UserRepository(SQLALchemyRepository):
    model = User

    async def get_many(self, user_ids: list[uuid.UUID]) -> list[User]:
        async with async_session_maker() as session:
            query = select(User).filter(User.id.in_(user_ids))
            res = await session.execute(query)
            return res.scalars().all()
