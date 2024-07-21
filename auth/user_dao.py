from datetime import datetime, timedelta

import jwt
import pyotp
from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.repository import UserRepository
from database import get_async_session
from auth.models.db import User
from config import settings
from auth.models.schemas import LoginUserResponseSuccessResult


class UserDAO:
    """Class for accessing user table."""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        if not isinstance(session, AsyncSession):
            raise ValueError("session is not instance of AsyncSession")
        self.session = session

    async def get_all_users(self) -> list[User]:
        """
        Retrieves all user records from the database and returns them as a list of User objects.
        :return: A list of User objects.
        :rtype: list[User]
        """
        raw_users = await self.session.execute(select(User))
        return list(raw_users.scalars().fetchall())

    async def create_user(self, email: str, password: str, full_name: str, birthdate: datetime, gender: str) -> User:
        """
        Creates a new user record in the database with the given email, password, and service.
        Also creates a corresponding entry in the UserCreateHistory table.

        :param gender: The user's gender.
        :param birthdate: The user's birthdate.
        :param full_name: The user's full name address.
        :param email: The user's email address.
        :param password: The user's password.
        :return: The User object representing the new user record.
        """
        user_dict = {"email": email, "hashed_password": password, "full_name": full_name,
                     "birthdate": birthdate, "gender": gender, "avatar_id": 1}
        user = await UserRepository().add_one(user_dict)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieves a User object from the database with the given email.

        :param email: The email address of the user to retrieve.
        :return: The User object for the specified email, or None if no such user exists.
        """
        user = (await self.session.execute(select(User).filter_by(email=email))).scalar()
        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Retrieves a User object from the database with the given ID.

        :param user_id: The ID of the user to retrieve.
        :return: The User object for the specified ID, or None if no such user exists.
        """
        try:
            user = (await self.session.execute(select(User).filter_by(id=user_id))).scalar()
        except DBAPIError:
            return None
        return user

    async def create_tokens(
            self,
            email: str | None = None,
            user_id: str | None = None,
    ) -> LoginUserResponseSuccessResult:
        """
        Creates new access and refresh tokens for the user with the given email or user ID.

        :param email: (optional) The email address of the user.
        :param user_id: (optional) The ID of the user.
        :return: A LoginUserResponseSuccessResult object containing the new access and refresh tokens, or a
                 LoginUserResponseSuccessResult object in which both tokens are None if the user is not found.
        """
        if email:
            user = (await self.session.execute(select(User).filter_by(email=email))).scalar()
        else:
            user = (await self.session.execute(select(User).filter_by(id=user_id))).scalar()
        if not user:
            return LoginUserResponseSuccessResult(**{"access_token": None, "refresh_token": None})  # type: ignore
        res = LoginUserResponseSuccessResult(
            **{
                "access_token": self.generate_jwt_token(
                    token_type="access",
                    user_id=str(user.id),
                    token_ttl=settings.JWT_ACCESS_TTL,
                ),
                "refresh_token": self.generate_jwt_token(
                    token_type="refresh",
                    user_id=str(user.id),
                    token_ttl=settings.JWT_REFRESH_TTL,
                ),
            }
        )
        return res

    @staticmethod
    def generate_jwt_token(token_type: str, user_id: str, token_ttl: int, secret_key: str | None = None) -> str:
        """
        Generates a JWT token with the specified token type, user ID, and time-to-live (TTL).

        :param token_type: The type of token, such as "access" or "refresh".
        :param user_id: The ID of the user for whom the token is being created.
        :param token_ttl: The duration of the token's lifetime in seconds.
        :param secret_key: (optional) The secret key to use for encoding the token. If not provided, the default
        secret key in the settings module is used.
        :return: A string representation of the encoded JWT token.
        """
        payload = {
            "type": token_type,
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=token_ttl),
        }
        if not secret_key:
            token = jwt.encode(payload, settings.SECRET, algorithm="HS256")
        else:
            token = jwt.encode(payload, secret_key, algorithm="HS256")
        return str(token)

    async def update_user(self, user_id: str, user_data: dict) -> User | None:
        """
        Updates a user record in the database with the given data.

        :param user_id: The ID of the user to update.
        :param user_data: A dictionary containing the updated user data.
        :return: The updated User object, or None if the user does not exist.
        """
        try:
            user = await self.get_user_by_id(user_id)
            if user is None:
                return None
            await self.session.execute(
                update(User)
                .where(User.id == user_id)
                .values(**user_data)
            )
            await self.session.commit()
            return await self.get_user_by_id(user_id)
        except DBAPIError as e:
            await self.session.rollback()
            raise e
