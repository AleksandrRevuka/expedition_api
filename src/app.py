from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import click
from fastapi import FastAPI
from sqlalchemy.orm import clear_mappers
from starlette.middleware.cors import CORSMiddleware

from src.adapters.database.config import get_database_config
from src.adapters.database.db import AsyncDatabaseSQLAlchemyManager
from src.adapters.database.models._all_mappers import mappers
from src.all_routers import api_router
from src.common.container.main_container import Container
from src.common.exceptions.global_error_handler import GlobalErrorHandler
from src.conf.app_config import get_cors_config
from src.conf.logging_config import LOGGER

COLOR_URL = click.style("http://127.0.0.1:8000/docs", bold=True, fg="green", italic=True)
MESSAGE = f"Open {COLOR_URL} to start 'Expedition API'"


class CustomFastAPI(FastAPI):
    """FastAPI subclass that carries a reference to the DI container."""

    def __init__(self, *args: Any, container: Container, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.container: Container = container


@asynccontextmanager
async def lifespan(app: CustomFastAPI) -> AsyncGenerator[None, None]:
    container = app.container

    db: AsyncDatabaseSQLAlchemyManager = container.core.db_manager()
    await db.connect(echo=get_database_config().DATABASE_ECHO)
    db.init_session_factory()

    for mapper in mappers:
        mapper()

    yield

    clear_mappers()
    await db.disconnect()
    LOGGER.info("FastAPI app stopped", app_id=id(app))


def create_app() -> CustomFastAPI:
    LOGGER.info(MESSAGE)

    container = Container()
    container.check_dependencies()
    container.core.init_resources()

    cors = get_cors_config()

    app = CustomFastAPI(
        title="Expedition API",
        swagger_ui_parameters={"operationsSorter": "method"},
        container=container,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors.ALLOW_ORIGINS,
        allow_credentials=cors.ALLOW_CREDENTIALS,
        allow_methods=cors.ALLOW_METHODS,
        allow_headers=cors.ALLOW_HEADERS,
    )

    GlobalErrorHandler().register_all_handlers(app)

    app.include_router(api_router)

    LOGGER.info("FastAPI started", app_id=id(app))
    return app


app = create_app()
