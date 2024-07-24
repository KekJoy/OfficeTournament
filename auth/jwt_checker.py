import datetime
import uuid

import jwt
from fastapi import Depends, HTTPException
from starlette import status
from starlette.requests import Request

from auth.user_dao import UserDAO
from auth.models.db import User
from config import settings


async def check_jwt(request: Request, user_dao: UserDAO = Depends()) -> User:
    """
    Access token check
    :param request:
    :param user_dao:
    :return:
    """
    user_token = request.headers.get("Authorization")
    user_id = check_token_payload_and_get_user_id(user_token, token_type="access")
    user = await user_dao.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized7"})
    return user


async def check_jwt_refresh(request: Request, user_dao: UserDAO = Depends()) -> User:
    """
    Refresh token check
    :param request:
    :param user_dao:
    :return:
    """
    user_token = request.headers.get("Authorization")
    user_id = check_token_payload_and_get_user_id(user_token, token_type="refresh")
    user = await user_dao.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized"})
    return user


def check_token_payload_and_get_user_id(token: str | None, token_type: str) -> str:
    """
    jwt token validation
    :param token:
    :param token_type:
    :return: user_id
    """
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized1"})
    try:
        jwt_decode = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
    except jwt.DecodeError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"detail": "Unauthorized2", "error": str(e)})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"detail": "Unauthorized3", "error": "Token has expired"})
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"detail": "Unauthorized2", "error": "Invalid token"})
    user_id = jwt_decode.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized4"})
    if jwt_decode.get("type") != token_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized5"})
    if jwt_decode["exp"] < datetime.datetime.utcnow().timestamp():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized6"})
    return user_id
