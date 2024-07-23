import uuid

from auth.repository import UserRepository
from grid_generator.models.schemas import GridUserSchema


async def get_users_dict(users_id: list[uuid.UUID]) -> dict[uuid.UUID, GridUserSchema]:
    data = await UserRepository().get(users_id)
    users = [GridUserSchema(**user.__dict__) for user in data]
    return {user.id: user for user in users}


def get_id_dict(items: list):
    return {item.id: item for item in items}


def to_dict_list(objects: list) -> list[dict]:
    return [x.__dict__ for x in objects]
