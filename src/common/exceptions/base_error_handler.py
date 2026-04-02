from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.common.exceptions.exc_utils import exc_name, log_wrapper
from src.common.schemas.responses import ErrorResponse


class BaseErrorHandler:
    """Centralized exception handler for a set of exception types."""

    def __init__(self, exception_status_map: dict[type[Exception], int]) -> None:
        self.exception_status_map = exception_status_map

    def create_handler(
        self, app: FastAPI
    ) -> Callable[[Request, Exception], Coroutine[Any, Any, JSONResponse]]:
        async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
            status_code = self.exception_status_map.get(type(exc), 500)
            log_wrapper(request, exc, status_code)
            return JSONResponse(
                status_code=status_code,
                content=ErrorResponse.respond(
                    message=str(exc),
                    exception=exc_name(exc),
                ),
            )

        return exception_handler

    def register_handlers(self, app: FastAPI) -> None:
        handler = self.create_handler(app)
        for exception_class in self.exception_status_map:
            app.exception_handler(exception_class)(handler)
