from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parents[2]


class BaseSet(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        extra="ignore",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )
