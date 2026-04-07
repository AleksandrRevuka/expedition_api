from typing import Callable, Any, Coroutine
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from src.modules.expeditions.application.commands.commands import InviteMemberCommand
from src.modules.expeditions.application.use_cases.invite_member import InviteMemberUseCase
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionAccessDeniedError,
    ExpeditionNotFoundError,
    MemberAlreadyInvitedError,
)
from tests.config import CHIEF_ID, EXPEDITION_ID, MEMBER_ID

pytestmark = pytest.mark.unit


class TestInviteMemberUseCase:

    @pytest.mark.asyncio
    async def test_invite_member_success(
        self, mocker: MockerFixture, expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]
    ) -> None:
        expedition = await expedition_factory()

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )
        result = await use_case(command)

        assert result == expedition
        assert len(result.members) == 1
        mock_members.add_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_invite_member_expedition_not_found_raises_error(self, mocker: MockerFixture) -> None:
        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = None

        mock_members = mocker.AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_invite_member_wrong_chief_raises_error(
        self, mocker: MockerFixture, expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]]
    ) -> None:
        expedition = await expedition_factory()

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=uuid4(),
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionAccessDeniedError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_invite_member_already_invited_raises_error(
        self,
        mocker: MockerFixture,
        expedition_factory: Callable[..., Coroutine[Any, Any, ExpeditionAggregate]],
        member_factory: Callable[..., Coroutine[Any, Any, ExpeditionMemberEntity]],
    ) -> None:
        member = await member_factory()
        expedition = await expedition_factory(members=[member])

        mock_expeditions = mocker.AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = mocker.AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )

        with pytest.raises(MemberAlreadyInvitedError):
            await use_case(command)
