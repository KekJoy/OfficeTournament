from fastapi import Depends, Header

from auth.service import auth_router
from auth.user_dao import UserDAO
from auth.models.db import User
from auth.jwt_checker import check_jwt, check_jwt_refresh
from auth.models.schemas import RefreshTokenResponse, UserResponse


@auth_router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(check_jwt), Authorization: str = Header()) -> UserResponse:
    """
    Getting a user
    """
    return UserResponse(status="OK", result={"user_id": user.id})  # type: ignore


@auth_router.get("/refresh_token", response_model=RefreshTokenResponse)
async def get_refresh_token(
        user: User = Depends(check_jwt_refresh),
        user_dao: UserDAO = Depends(),
        Authorization: str = Header(),
) -> RefreshTokenResponse:
    """
    Getting an access token through a refresh
    """
    access_token = user_dao.generate_jwt_token(token_type="access", user_id=str(user.id), token_ttl=60 * 60)
    refresh_token = user_dao.generate_jwt_token(token_type="refresh", user_id=str(user.id), token_ttl=60 * 60 * 60)
    return RefreshTokenResponse(
        status="OK",  # type: ignore
        result={"access_token": access_token, "refresh_token": refresh_token},  # type: ignore
    )
