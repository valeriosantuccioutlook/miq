import os
from datetime import timedelta
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Postgre
    DB_USER: str
    DB_NAME: str
    DB_PSW: str
    DB_HOST: str
    DB_PORT: int
    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PSW: str | None = None
    # User access
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int

    @property
    def DB_URI(cls) -> str:
        if os.environ.get("DB_URI") is None:
            return f"postgresql://{cls.DB_USER}:{cls.DB_PSW}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        return os.environ["DB_URI"]

    @property
    def RATE_LIMIT_DURATION(cls) -> timedelta:
        mins: str | int = os.environ.get("RATE_LIMIT_DURATION", default=1)
        if isinstance(mins, str):
            mins = int(mins)
        return timedelta(minutes=mins)

    @property
    def RATE_LIMIT_REQUESTS(cls) -> int:
        lim: str | int = os.environ.get("RATE_LIMIT_REQUESTS", default=10)
        if isinstance(lim, str):
            lim = int(lim)
        return lim


@lru_cache
def _settings() -> Settings:
    return Settings()


settings: Settings = _settings()
