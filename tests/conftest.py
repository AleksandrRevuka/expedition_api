import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.exc import ArgumentError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from src.adapters.database.config import get_database_config as _get_db_cfg
from src.adapters.database.db import AsyncDatabaseSQLAlchemyManager
from src.adapters.database.models._all_mappers import mappers
from src.all_routers import api_router
from src.app import CustomFastAPI
from src.common.container.main_container import Container
from src.common.exceptions.global_error_handler import GlobalErrorHandler
from src.conf.enums import Role
from src.conf.security_conf import get_jwt_config
from src.modules.users.domain.aggregates.user import UserAggregate
from src.modules.users.infrastructure.password_service import PasswordService
from src.modules.users.infrastructure.token_service import TokenService
from src.modules.users.infrastructure.units_of_work import UsersStorageUnitOfWork


database_config = _get_db_cfg()


def drop_test_db() -> None:
    name_base = os.path.join(os.getcwd(), f"{database_config.DATABASE_NAME}_test.sqlite")
    for suffix in ("", "-wal", "-shm"):
        path = name_base + suffix
        if os.path.exists(path):
            os.remove(path)


@pytest_asyncio.fixture()
async def db_manager() -> AsyncGenerator[AsyncDatabaseSQLAlchemyManager, None]:
    """A fixture for creating a sessionable database manager."""
    db_manager = AsyncDatabaseSQLAlchemyManager(db_uri=database_config.ASYNC_TEST_SQL_LIGHT_URL)
    await db_manager.connect(connect_args={"check_same_thread": False}, poolclass=NullPool)
    db_manager.init_session_factory()

    try:
        yield db_manager
    finally:
        await db_manager.disconnect()


@pytest_asyncio.fixture
async def test_db(db_manager: AsyncDatabaseSQLAlchemyManager) -> AsyncGenerator[None, None]:
    """Create test db for tests."""
    await db_manager.create_database()
    yield
    await db_manager.engine.dispose()
    drop_test_db()


@pytest.fixture
def map_models_to_orm(test_db: None) -> None:
    """Create mappings from models to ORM according to DDD."""
    try:
        for mapper in mappers:
            mapper()
    except ArgumentError:
        pass


@pytest_asyncio.fixture
async def async_session(
    map_models_to_orm: None,
    db_manager: AsyncDatabaseSQLAlchemyManager,
) -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.session() as session:
        yield session


@pytest.fixture
def test_container(db_manager: AsyncDatabaseSQLAlchemyManager) -> Container:
    container = Container()
    container.core.db_manager.override(db_manager)
    return container


@pytest_asyncio.fixture
async def test_app(test_container: Container) -> CustomFastAPI:
    """Create a test app instance with the test container."""
    app = CustomFastAPI(container=test_container)
    app.container = test_container

    app.add_middleware(SessionMiddleware, secret_key=get_jwt_config().JWT_TOKEN_SECRET_KEY)

    error_handler = GlobalErrorHandler()
    error_handler.register_all_handlers(app)

    app.include_router(api_router)
    return app


@pytest_asyncio.fixture
async def async_client(
    test_app: CustomFastAPI,
    map_models_to_orm: None,
) -> AsyncGenerator[AsyncClient, None]:
    """Creates test app client for end-to-end tests."""
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture
def token_service() -> TokenService:
    return TokenService()


@pytest.fixture
def access_token(token_service: TokenService) -> str:
    email = "test@gmail.com"
    return token_service.create_access_token(email)


@pytest_asyncio.fixture
async def test_user(
    map_models_to_orm: None,
    db_manager: AsyncDatabaseSQLAlchemyManager,
) -> UserAggregate:
    async with UsersStorageUnitOfWork(db_manager.session_factory) as uow:
        user = UserAggregate.create(
            name="test_username",
            email="test@gmail.com",
            hashed_password=PasswordService().hash("password"),
            role=Role.member,
        )
        await uow.users.add_one(user)
        await uow.commit()
    return user
