from collections.abc import Callable, Coroutine
from typing import Any
from uuid import uuid4

import pytest
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.domain.exceptions.exceptions import (
    InvalidMemberStateTransitionError,
    MemberConfirmAccessDeniedError,
)

from src.conf.enums import MemberState
from tests.config import MEMBER_ID

pytestmark = pytest.mark.unit


class TestMemberEntity:

    @pytest.mark.asyncio
    async def test_create_member_success(
        self, member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]
    ) -> None:
        member = await member_factory(user_id=MEMBER_ID)

        assert member.state == MemberState.invited
        assert member.user_id == MEMBER_ID

    @pytest.mark.asyncio
    async def test_confirm_member_success(
        self, member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]
    ) -> None:
        member = await member_factory(state=MemberState.invited)
        member.confirm(MEMBER_ID)

        assert member.state == MemberState.confirmed

    @pytest.mark.asyncio
    async def test_confirm_member_not_invited_raises_error(
        self, member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]
    ) -> None:
        member = await member_factory(state=MemberState.confirmed)

        with pytest.raises(InvalidMemberStateTransitionError):
            member.confirm(MEMBER_ID)

    @pytest.mark.asyncio
    async def test_confirm_member_confirm_access_denied_raises_error(
        self, member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]]
    ) -> None:
        member = await member_factory(user_id=MEMBER_ID)

        with pytest.raises(MemberConfirmAccessDeniedError):
            member.confirm(uuid4())
