import uuid
from datetime import datetime
from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    email: str
    full_name: str
    birthdate: datetime
    gender: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    email: str
    password: str
    full_name: str
    birthdate: datetime
    gender: str
    avatar_id: int
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[str] = None
    full_name: Optional[str] = None
    birthdate: Optional[datetime] = None
    gender: Optional[str] = None
    avatar_id: Optional[int] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
