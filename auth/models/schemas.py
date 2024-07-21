import re
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

import bcrypt
from pydantic import BaseModel, Field, validator


class Status(str, Enum):
    OK = "OK"
    FAIL = "FAIL"


class Response(BaseModel):
    status: Status
    result: Any


class UserResponseResult(BaseModel):
    user_id: UUID


class UserResponse(Response):
    result: UserResponseResult


class RefreshTokenResponseResult(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenResponse(Response):
    result: RefreshTokenResponseResult


class CreateUserRequest(BaseModel):
    email: str = Field(description="User email")
    password: str = Field(description="User password")
    full_name: str = Field(description="User full name")
    birthdate: datetime
    gender: str

    @validator("email")
    def validate_email(cls, value: str) -> str:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Неверный формат email")
        return value

    # @validator("password")
    # def validate_password(cls, value: str) -> str:
    #     try:
    #         bcrypt.checkpw(b"hj", value.encode("utf-8"))
    #     except ValueError:
    #         raise ValueError("Неверный формат пароля")
    #     return value

    class Config:
        from_attributes = True
        json_json_schema_extra = {
            "example": {
                "email": "user@example.ru",
                "password": "$2b$12$qYVpdWQf7zN24z3hXEUTtuDp02UoFCBMY3y448iVHUWfox/MPEGvq",
            }
        }


class CreateUserResponseResult(BaseModel):
    user_id: UUID = Field(description="user id, used for identification in all services")


class CreateUserResponse(Response):
    result: CreateUserResponseResult


class LoginUserRequest(BaseModel):
    email: str = Field(description="User email")
    password: str = Field(description="User password")

    class Config:
        from_attributes = True
        json_json_schema_extra = {
            "example": {
                "email": "user@example.ru",
                "password": "123456",
            }
        }


class LoginUserResponseNeed2FAResult(BaseModel):
    detail: str
    token: str = Field(description="The token is used to validate 2fa")

    class Config:
        json_json_schema_extra = {
            "example": {
                "detail": "Требуется 2fa",
                "token": "jwt_token",
            }
        }


class LoginUserResponseSuccessResult(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "jwt_token",
                "refresh_token": "jwt_token",
            }
        }


class LoginUserResponseSuccess(Response):
    result: LoginUserResponseSuccessResult


class LoginUserResponse2FA(Response):
    result: LoginUserResponseNeed2FAResult
