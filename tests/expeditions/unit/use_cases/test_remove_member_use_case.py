import pytest
from unittest.mock import AsyncMock

from src.modules.expeditions.application.commands.commands import RemoveMemberCommand
from src.modules.expeditions.application.use_cases.remove_member import (
    RemoveMemberUseCase,
)
from src.modules.expeditions.domain.exceptions.exceptions import (
    ExpeditionAccessDeniedError,
    ExpeditionNotFoundError,
)
from tests.config import (
    CHIEF_ID,
    EXPEDITION_ID,
    MEMBER_ID,
    make_expedition,
    make_expedition_member,
)

pytestmark = pytest.mark.unit


class TestRemoveMemberUseCase:

    @pytest.mark.asyncio
    async def test_remove_member_success(self) -> None:
        member = make_expedition_member()
        expedition = make_expedition(members=[member])

        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = AsyncMock()

        use_case = RemoveMemberUseCase(mock_expeditions, mock_members)
        command = RemoveMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )
        result = await use_case(command)

        assert result == expedition
        assert len(result.members) == 0
        mock_members.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_expedition_not_found_raises_error(self) -> None:
        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = None

        mock_members = AsyncMock()

        use_case = RemoveMemberUseCase(mock_expeditions, mock_members)
        command = RemoveMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=CHIEF_ID,
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionNotFoundError):
            await use_case(command)

    @pytest.mark.asyncio
    async def test_remove_member_wrong_chief_raises_error(self) -> None:
        from uuid import uuid4

        member = make_expedition_member()
        expedition = make_expedition(members=[member])

        mock_expeditions = AsyncMock()
        mock_expeditions.get_one_with_relationships.return_value = expedition

        mock_members = AsyncMock()

        use_case = RemoveMemberUseCase(mock_expeditions, mock_members)
        command = RemoveMemberCommand(
            expedition_id=EXPEDITION_ID,
            chief_id=uuid4(),
            user_id=MEMBER_ID,
        )

        with pytest.raises(ExpeditionAccessDeniedError):
            await use_case(command)
