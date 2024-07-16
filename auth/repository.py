from auth.models.db import User
from utils.repository import SQLALchemyRepository


class UserRepository(SQLALchemyRepository):
    model = User
