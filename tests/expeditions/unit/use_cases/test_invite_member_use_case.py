import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.commands.commands import InviteMemberCommand
from src.modules.expeditions.application.use_cases.invite_member import (
    InviteMemberUseCase,
)
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionAccessDeniedError,
    ExpeditionNotFoundError,
    MemberAlreadyInvitedError,
)
from tests.config import CHIEF_ID, EXPEDITION_ID, MEMBER_ID, make_expedition

pytestmark = pytest.mark.unit


class TestInviteMemberUseCase:

    @pytest.mark.asyncio
    async def test_invite_member_success(self) -> None:
        expedition = make_expedition()

        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = AsyncMock()

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
    async def test_invite_member_expedition_not_found_raises_error(self) -> None:
        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = None

        mock_members = AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_invite_member_wrong_chief_raises_error(self) -> None:
        from uuid import uuid4

        expedition = make_expedition()

        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=uuid4(),
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionAccessDeniedError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_invite_member_already_invited_raises_error(self) -> None:
        from tests.config import make_expedition_member

        member = make_expedition_member()
        expedition = make_expedition(members=[member])

        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = AsyncMock()

        use_case = InviteMemberUseCase(mock_expeditions, mock_members)
        command = InviteMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )

        with pytest.raises(MemberAlreadyInvitedError):
            await use_case(command)
