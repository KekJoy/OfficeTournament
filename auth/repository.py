import uuid

from auth.models.db import User
from utils.repository import SQLALchemyRepository
from sqlalchemy import select

from database import async_session_maker


class UserRepository(SQLALchemyRepository):
    model = User
