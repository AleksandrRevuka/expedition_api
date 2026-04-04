import os
from enum import StrEnum
from functools import lru_cache

from src.conf.base_config import BaseSet


class Dialect(StrEnum):
    postgresql = "postgresql"
    docker_postgres = "docker_postgres"
    sqlite = "sqlite"


class Driver(StrEnum):
    asyncpg = "asyncpg"
    psycopg2 = "psycopg2"
    aiosqlite = "aiosqlite"


class DatabaseConfig(BaseSet):
    DATABASE_DIALECT: Dialect = Dialect.postgresql

    DATABASE_HOST: str = "expedition-postgres"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = "expedition"

    DATABASE_ECHO: bool = False
    DATABASE_AUTO_FLUSH: bool = False
    DATABASE_AUTO_COMMIT: bool = False
    DATABASE_EXPIRE_ON_COMMIT: bool = False

    @property
    def ASYNC_DB_URL(self) -> str:
        return (
            f"{self.DATABASE_DIALECT}+{Driver.asyncpg}://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def SYNC_DB_URL(self) -> str:
        return (
            f"{self.DATABASE_DIALECT}+{Driver.psycopg2}://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def ASYNC_TEST_SQL_LIGHT_URL(self) -> str:
        return f"{Dialect.sqlite}+{Driver.aiosqlite}:///" + os.path.join(
            os.getcwd(), f"{self.DATABASE_NAME}_test.sqlite"
        )


@lru_cache
def get_database_config() -> DatabaseConfig:
    return DatabaseConfig()
