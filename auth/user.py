from fastapi import Depends, Header, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.service import auth_router
from auth.user_dao import UserDAO
from auth.models.db import User
from auth.jwt_checker import check_jwt, check_jwt_refresh
from auth.models.schemas import RefreshTokenResponse, UserResponse, UserResponseModel, UserUpdateModel
from database import get_async_session

user_router = APIRouter(tags=["User Profile"])


@user_router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(check_jwt), Authorization: str = Header()) -> UserResponse:
    """
    Getting a user
    """
    return UserResponse(status="OK", result={"user_id": user.id})  # type: ignore


@user_router.get("/refresh_token", response_model=RefreshTokenResponse)
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


@user_router.get("/user/{user_id}", response_model=UserResponseModel)
async def get_user_by_id(user_id: str, session: AsyncSession = Depends(get_async_session)) -> UserResponseModel:
    """
    Endpoint to get a user by ID.
    :param user_id: The ID of the user to retrieve.
    :param session: The database session.
    :param Authorization: The authorization token.
    :return: A UserResponseModel containing the user's information.
    """
    user_dao = UserDAO(session)
    user = await user_dao.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = user.__dict__
    user_dict['id'] = str(user_dict['id'])

    return UserResponseModel(**user_dict)


@user_router.patch("/update/{user_id}", response_model=UserResponseModel)
async def update_user_profile(user_id: str, user_update: UserUpdateModel,
                              session: AsyncSession = Depends(get_async_session)) -> UserResponseModel:
    """
    Endpoint to update a user's profile.
    :param user_id: The ID of the user to update.
    :param user_update: The updated user data.
    :param session: The database session.
    :param Authorization: The authorization token.
    :return: A UserResponseModel containing the updated user's information.
    """
    user_dao = UserDAO(session)
    updated_user = await user_dao.update_user(user_id, user_update.dict(exclude_unset=True))
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = updated_user.__dict__
    user_dict['id'] = str(user_dict['id'])

    return UserResponseModel(**user_dict)
