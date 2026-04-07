import pytest_asyncio

from src.modules.users.domain.aggregates.user import UserAggregate


@pytest_asyncio.fixture
async def test_user(user_factory) -> UserAggregate:
    return await user_factory(email="test@gmail.com", persist=True)
