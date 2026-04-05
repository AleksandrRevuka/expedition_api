import pytest
from unittest.mock import AsyncMock

from src.conf.enums import MemberState
from src.modules.expeditions.application.commands.commands import ConfirmMemberCommand
from src.modules.expeditions.application.use_cases.confirm_member import (
    ConfirmMemberUseCase,
)
from src.modules.expeditions.domain.exceptions.exceptions import ExpeditionNotFoundError
from tests.config import (
    EXPEDITION_ID,
    MEMBER_ID,
    make_expedition,
    make_expedition_member,
)

pytestmark = pytest.mark.unit


class TestConfirmMemberUseCase:

    @pytest.mark.asyncio
    async def test_confirm_member_success(self) -> None:
        member = make_expedition_member(state=MemberState.invited)
        expedition = make_expedition(members=[member])

        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = AsyncMock()

        use_case = ConfirmMemberUseCase(mock_expeditions, mock_members)
        command = ConfirmMemberCommand(
            expedition_id=EXPEDITION_ID,
            user_id=MEMBER_ID,
        )
        result = await use_case(command)

        assert result == expedition
        assert result.members[0].state == MemberState.confirmed
        mock_members.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_member_expedition_not_found_raises_error(self) -> None:
        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = None

        mock_members = AsyncMock()

        use_case = ConfirmMemberUseCase(mock_expeditions, mock_members)
        command = ConfirmMemberCommand(
            expedition_id=EXPEDITION_ID,
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)
