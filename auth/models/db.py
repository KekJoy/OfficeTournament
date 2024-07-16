import uuid

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String, DateTime, func, UUID, Boolean
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base, get_async_session


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    contact_inf = Column(String, nullable=True)
    gender = Column(String, nullable=False)
    birthdate = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    avatar_id = Column(Integer, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
