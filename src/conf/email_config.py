from functools import lru_cache

from fastapi_mail import ConnectionConfig
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from src.conf.app_config import get_path_config
from src.conf.base_config import BaseSet


class MailConfig(BaseSet, BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str


@lru_cache
def get_mail_config() -> MailConfig:
    return MailConfig()  # type: ignore


@lru_cache
def get_mail_conf() -> ConnectionConfig:
    mail_cfg = get_mail_config()
    path_cfg = get_path_config()
    return ConnectionConfig(
        MAIL_USERNAME=mail_cfg.MAIL_USERNAME,
        MAIL_PASSWORD=mail_cfg.MAIL_PASSWORD,
        MAIL_FROM=mail_cfg.MAIL_FROM,
        MAIL_PORT=mail_cfg.MAIL_PORT,
        MAIL_SERVER=mail_cfg.MAIL_SERVER,
        MAIL_FROM_NAME="Platforma 17",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=path_cfg.TEMPLATE_DIR,
    )


__all__ = [
    "MailConfig",
    "get_mail_config",
    "get_mail_conf",
]
