from dependency_injector import containers, providers

from src.adapters.database.config import get_database_config
from src.adapters.database.db import AsyncDatabaseSQLAlchemyManager
from src.modules.websocket.manager import ExpeditionConnectionManager


class BaseContainer(containers.DeclarativeContainer):
    db_manager = providers.Singleton(
        AsyncDatabaseSQLAlchemyManager,
        db_uri=get_database_config().ASYNC_DB_URL,
    )

    ws_manager = providers.Singleton(ExpeditionConnectionManager)
