from functools import lru_cache

from src.conf.base_config import BaseSet
from src.conf.enums import Environment


class UvicornConfig(BaseSet):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "info"
    RELOAD: bool = True


class AppConfig(BaseSet):
    ENVIRONMENT: Environment = Environment.prod
    TIMEZONE: str = "UTC"


class CORSConfig(BaseSet):
    ALLOW_ORIGINS: list[str] = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    ALLOW_HEADERS: list[str] = [
        "Content-Type",
        "Authorization",
    ]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = ["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"]


@lru_cache
def get_uvicorn_config() -> UvicornConfig:
    return UvicornConfig()


@lru_cache
def get_app_config() -> AppConfig:
    return AppConfig()


@lru_cache
def get_cors_config() -> CORSConfig:
    return CORSConfig()


__all__ = [
    "UvicornConfig",
    "AppConfig",
    "CORSConfig",
    "get_uvicorn_config",
    "get_app_config",
    "get_cors_config",
]
