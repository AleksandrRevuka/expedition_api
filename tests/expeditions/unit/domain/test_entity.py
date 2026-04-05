from uuid import uuid4
from src.modules.expeditions.domain.exceptions.exceptions import InvalidMemberStateTransitionError, MemberConfirmAccessDeniedError
from src.conf.enums import MemberState
from tests.config import make_expedition_member, MEMBER_ID
import pytest

pytestmark = pytest.mark.unit


class TestMemberEntity:
    def test_create_member_success(self):
        member = make_expedition_member()

        assert member.id == MEMBER_ID
        assert member.state == MemberState.invited
    
    def test_confirm_member_success(self):
        member = make_expedition_member(state=MemberState.invited)
        member.confirm(MEMBER_ID)

        assert member.state == MemberState.confirmed

    def test_confirm_member_not_invited_raises_error(self):
        member = make_expedition_member(state=MemberState.confirmed)

        with pytest.raises(InvalidMemberStateTransitionError):
            member.confirm(MEMBER_ID)

    def test_confirm_member_confirm_access_denied_raises_error(self):
        member = make_expedition_member(user_id=MEMBER_ID)

        with pytest.raises(MemberConfirmAccessDeniedError):
            member.confirm(uuid4())