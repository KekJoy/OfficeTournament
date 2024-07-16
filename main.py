from fastapi import FastAPI

from auth.manager import fastapi_users
from auth.models.schemas import UserRead, UserCreate
from auth.service import auth_backend
from tournaments.service import tournament_router

app = FastAPI(title="Office Tournament")


@app.post("/")
async def root():
    return {"message": "Hello World"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(tournament_router, prefix='/tournament', tags=['tournaments'])
