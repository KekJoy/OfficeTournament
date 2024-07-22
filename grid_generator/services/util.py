import uuid

from auth.repository import UserRepository
from grid_generator.models.schemas import GridUserSchema


async def get_users_dict(users_id: list[uuid.UUID]) -> dict[uuid.UUID, GridUserSchema]:
    data = await UserRepository().get_many(users_id)
    users = [GridUserSchema(**user.__dict__) for user in data]
    return {user.id: user for user in users}


def to_dict_list(objects: list) -> list[dict]:
    return [x.__dict__ for x in objects]