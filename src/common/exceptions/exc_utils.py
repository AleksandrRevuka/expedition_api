import traceback
from types import TracebackType

from fastapi import Request

from src.conf.logging_config import LOGGER


def exc_name(ex: Exception) -> str:
    return f"{ex.__class__.__name__}: {ex}"


def exc_name_without_ex(exc: Exception) -> str:
    return f"{exc.__class__.__name__}"


def log_wrapper(request: Request, exc: Exception, status_code: int) -> None:
    tb: TracebackType | None = exc.__traceback__
    LOGGER.error(
        f"HTTP {status_code} Error",
        status_code=status_code,
        method=request.method,
        url=str(request.url),
        exception_type=exc_name_without_ex(exc),
    )
    if tb:
        tb_lines = traceback.format_tb(tb)
        if tb_lines:
            LOGGER.debug("Exception traceback", traceback=tb_lines[-1])
