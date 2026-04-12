from collections.abc import Callable, Coroutine
from typing import Any

import pytest
from src.modules.users.domain.aggregates.user import UserAggregate

from src.conf.enums import Role

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


class TestUserAggregate:

    async def test_create_user_aggregate_success(
        self, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory()

        assert isinstance(user, UserAggregate)
        assert user.email == "test@gmail.com"
        assert user.name == "test_username"
        assert user.role == Role.member

    async def test_is_chief_user_aggregate_success(
        self, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory(role=Role.chief)

        assert isinstance(user, UserAggregate)
        assert user.is_chief()
        assert not user.is_member()

    async def test_is_member_user_aggregate_success(
        self, user_factory: Callable[..., Coroutine[Any, Any, UserAggregate]]
    ) -> None:
        user = await user_factory(role=Role.member)

        assert isinstance(user, UserAggregate)
        assert user.is_member()
        assert not user.is_chief()
