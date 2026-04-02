from functools import lru_cache

from src.conf.base_config import BaseSet


class JWTConfig(BaseSet):
    JWT_TOKEN_SECRET_KEY: str = "dev-only-secret-key-override-in-production"
    JWT_TOKEN_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINS: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7


@lru_cache
def get_jwt_config() -> JWTConfig:
    return JWTConfig()


__all__ = ["JWTConfig", "get_jwt_config"]
