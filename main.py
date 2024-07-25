from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth.service import auth_router
from auth.user import user_router
from config import settings
from grid_generator.services.grid import grid_router
from tournaments.services.sport import sport_router
from tournaments.services.tournament import tournament_router
from tournaments.services.user_actions import user_actions

app = FastAPI(title="Office Tournament")

@app.post("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router, tags=['Auth'])
app.include_router(tournament_router, tags=['Tournaments'])
app.include_router(sport_router, tags=['Sport'])
app.include_router(grid_router, tags=['Grids'])
app.include_router(user_router, tags=['User Profile'])
app.include_router(user_actions, tags=["User Actions"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://80.87.193.173", "https://80.87.193.173", "null", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
