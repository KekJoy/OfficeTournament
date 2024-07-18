import uuid
from typing import Optional

import jwt
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin, FastAPIUsers

from auth.service import auth_backend
from config import settings
from auth.models.db import User, get_user_db

SECRET = settings.VERIFY_TOKEN_SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        await UserManager.request_verify(self, user, request)
        payload = {"email": user.email}
        token = jwt.encode(payload, self.verification_token_secret)
        print(f"User {user.id} has registered.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
