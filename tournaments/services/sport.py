from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Header

from auth.jwt_checker import check_jwt
from auth.models.db import User
from tournaments.models.schemas import CreateSportSchema, GetSportSchema
from tournaments.repository import SportRepository

sport_router = APIRouter(prefix='/sport', tags=['Sport'])


@sport_router.post("/create", response_model=GetSportSchema)
async def create_sport(sport: CreateSportSchema,
                       user: User = Depends(check_jwt), Authorization: str = Header()) -> GetSportSchema:
    """Создать вид спорта"""
    sport_id = await SportRepository().add_one(sport.model_dump())
    return GetSportSchema(id=sport_id, name=sport.name)


@sport_router.get("/", response_model=List[GetSportSchema])
async def get_sports(user: User = Depends(check_jwt), Authorization: str = Header()) -> List[GetSportSchema]:
    """Получить список всех видов спорта"""
    sports = await SportRepository().find_all()
    result = []
    for sport in sports:
        sport = sport.__dict__
        result.append(GetSportSchema(**sport))
    return result


@sport_router.get("/{id}", response_model=GetSportSchema)
async def get_sport(id: UUID, user: User = Depends(check_jwt), Authorization: str = Header()) -> GetSportSchema:
    """Получить вид спорта по ID"""
    sport = await SportRepository().find_one(record_id=id)
    sport = sport.__dict__
    return GetSportSchema(**sport)


@sport_router.patch("/update/{id}", response_model=GetSportSchema)
async def update_sport(id: UUID, sport: CreateSportSchema,
                       user: User = Depends(check_jwt), Authorization: str = Header()) -> GetSportSchema:
    """Обновить информацию о спорте"""
    if not SportRepository().find_one(record_id=id):
        raise HTTPException(status_code=404, detail="Sport not found")
    await SportRepository().update_one(record_id=id, data=sport.model_dump())
    return GetSportSchema(id=id, name=sport.name)


@sport_router.delete("/{id}", response_model=GetSportSchema)
async def delete_sport(id: UUID,
                       user: User = Depends(check_jwt), Authorization: str = Header()) -> GetSportSchema:
    """Удалить вид спорта"""
    sport = await SportRepository().find_one(record_id=id)
    try:
        await SportRepository().delete_one(record_id=id)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Sport not found")
    return GetSportSchema(**sport.__dict__)
