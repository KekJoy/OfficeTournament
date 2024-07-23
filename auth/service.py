import bcrypt
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException
from starlette import status
from starlette.requests import Request

from auth.user_dao import UserDAO
from auth.models.schemas import (
    CreateUserRequest,
    CreateUserResponse,
    LoginUserRequest,
    LoginUserResponse2FA,
    LoginUserResponseSuccess,
    Status,
)
from config import settings

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post("/create_user", response_model=CreateUserResponse)
async def create_user(
        user_request: CreateUserRequest,
        user_dao: UserDAO = Depends(),
        Authorization: str | None = Header(default=None),
) -> CreateUserResponse:
    """
    User registration endpoint\n
    """
    user = await user_dao.get_user_by_email(email=user_request.email)
    if user:
        return CreateUserResponse(
            **{"status": "OK", "result": {"user_id": user.id, "is_user_exists": True}}  # type: ignore
        )
    is_account_confirm = False
    if Authorization:
        is_account_confirm = True
    user = await user_dao.create_user(
        email=user_request.email.lower(),
        password=bcrypt.hashpw(user_request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        full_name=user_request.full_name,
        birthdate=user_request.birthdate,
        gender=user_request.gender,
    )
    return CreateUserResponse(
        **{"status": "OK", "result": {"user_id": user}}  # type: ignore
    )


@auth_router.post(
    "/login",
    response_model=LoginUserResponseSuccess,
    responses={403: {"model": LoginUserResponse2FA}},
)
async def login(user_request: LoginUserRequest, user_dao: UserDAO = Depends()) -> LoginUserResponseSuccess:
    """
    Endpoint for user login.
    """
    user = await user_dao.get_user_by_email(user_request.email.lower())
    if not user or not bcrypt.checkpw(user_request.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail={"detail": "Неверный логин или пароль"})
    result = await user_dao.create_tokens(email=user.email)
    return LoginUserResponseSuccess(status=Status.OK, result=result)


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, Authorization: str = Header()):
    """
    Endpoint for user logout. Invalidates the user's current token.
    """
    user_token = request.headers.get("Authorization")
    if not user_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized"})
    try:
        jwt_decode = jwt.decode(user_token, settings.SECRET, algorithms=["HS256"])
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized"})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized"})

    user_id = jwt_decode.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"detail": "Unauthorized"})
    return {"status": "success", "message": "Logged out successfully"}
