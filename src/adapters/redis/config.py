from functools import lru_cache

from src.conf.base_config import BaseSet


class RedisConfig(BaseSet):
    REDIS_PASSWORD: str | None = None
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_USER_TLL: int = 86400
    REDIS_REFRESH_TOKEN_TTL: int = 3600
    REDIS_ACCESS_TOKEN_TTL: int = 604800

    def get_redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


@lru_cache
def get_redis_config() -> RedisConfig:
    return RedisConfig()
