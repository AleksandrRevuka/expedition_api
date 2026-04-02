from fastapi import FastAPI

from src.common.exceptions.base_error_handler import BaseErrorHandler
from src.common.exceptions.error_registry import ERROR_STATUS_MAP


class GlobalErrorHandler:
    """Registers all application exception handlers into FastAPI."""

    def __init__(self) -> None:
        self.error_handler = BaseErrorHandler(ERROR_STATUS_MAP)

    def register_all_handlers(self, app: FastAPI) -> None:
        self.error_handler.register_handlers(app)
