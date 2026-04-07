from src.modules.websocket.manager import ExpeditionConnectionManager
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.infrastructure.units_of_work import ExpeditionsStorageUnitOfWork
from tests.config import CHIEF_ID, EXPEDITION_ID, PAST_DATE, MEMBER_ID, USER_ID
import uuid
from datetime import datetime, UTC
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from typing import Any
import os
from collections.abc import AsyncGenerator, Callable, Coroutine

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
from src.conf.enums import Role, ExpeditionStatus, MemberState
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
def access_token(token_service: TokenService) -> Callable[..., str]:

    def _create_access_token(email: str = "test@gmail.com") -> str:
        return token_service.create_access_token(email)

    return _create_access_token


@pytest.fixture
def password_service() -> PasswordService:
    return PasswordService()


@pytest.fixture
def ws_manager() -> ExpeditionConnectionManager:
    return ExpeditionConnectionManager()


@pytest_asyncio.fixture
async def user_factory(
    map_models_to_orm: None,
    db_manager: AsyncDatabaseSQLAlchemyManager,
    password_service: PasswordService,
) -> Callable[..., Coroutine[Any, Any, UserAggregate]]:
    async def _create_user(
        id: uuid.UUID = USER_ID,
        email: str = "test@gmail.com",
        name: str = "test_username",
        role: Role = Role.member,
        password: str = "password",
        persist: bool = False,
    ) -> UserAggregate:
        user = UserAggregate(
            id=id,
            name=name,
            email=email,
            hashed_password=password_service.hash(password),
            role=role,
        )
        if persist:
            async with UsersStorageUnitOfWork(db_manager.session_factory) as uow:
                await uow.users.add_one(user)
                await uow.commit()
        return user

    return _create_user


@pytest_asyncio.fixture
async def expedition_factory(
    map_models_to_orm: None,
    db_manager: AsyncDatabaseSQLAlchemyManager,
) -> Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]:
    async def _create_expedition(
        id: uuid.UUID = EXPEDITION_ID,
        title: str = "Test Expedition",
        description: str = "Test Description",
        status: ExpeditionStatus = ExpeditionStatus.draft,
        chief_id: uuid.UUID = CHIEF_ID,
        start_at: datetime = PAST_DATE,
        end_at: datetime | None = None,
        capacity: int = 5,
        members: list[ExpeditionMemberEntity] | None = None,
        persist: bool = False
    ) -> ExpeditionAggregate:
        expedition = ExpeditionAggregate(
            id=id,
            title=title,
            description=description,
            status=status,
            chief_id=chief_id,
            start_at=start_at,
            end_at=end_at,
            capacity=capacity,
            members=members or [],
        )
        if persist:
            async with ExpeditionsStorageUnitOfWork(db_manager.session_factory) as uow:
                await uow.expeditions.add_one(expedition)
                await uow.commit()
        return expedition

    return _create_expedition


@pytest_asyncio.fixture
async def member_factory(
    map_models_to_orm: None,
    db_manager: AsyncDatabaseSQLAlchemyManager,
) -> Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]:
    async def _create_member(
        expedition_id: uuid.UUID = EXPEDITION_ID,
        user_id: uuid.UUID = MEMBER_ID,
        state: MemberState = MemberState.invited,
        confirmed_at: datetime | None = None,
        persist: bool = False
    ) -> ExpeditionMemberEntity:
        member = ExpeditionMemberEntity(
            expedition_id=expedition_id,
            user_id=user_id,
            state=state,
            invited_at=datetime.now(UTC),
            confirmed_at=confirmed_at

        )
        if persist:
            async with ExpeditionsStorageUnitOfWork(db_manager.session_factory) as uow:
                await uow.members.add_one(member)
                await uow.commit()
        return member

    return _create_member