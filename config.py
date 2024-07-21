from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    SECRET: str
    VERIFY_TOKEN_SECRET: str

    JWT_ACCESS_TTL: int
    JWT_REFRESH_TTL: int

    ORIGINS: List[str] = []

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

class AppSettings:
    DEFAULT_GAME_COUNT = 3

    DEFAULT_MAX_TEAMS_COUNT = 16

app_settings = AppSettings()
