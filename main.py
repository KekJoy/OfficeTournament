from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth.service import auth_router
from config import settings
from grid_generator.services.grid import grid_router
from tournaments.services.sport import sport_router
from tournaments.services.tournament import tournament_router

app = FastAPI(title="Office Tournament")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
async def root():
    return {"message": "Hello World"}

app.include_router(auth_router, tags=['auth'])
app.include_router(tournament_router, tags=['tournaments'])
app.include_router(sport_router, tags=['sport'])
app.include_router(grid_router, tags=['grids'])
