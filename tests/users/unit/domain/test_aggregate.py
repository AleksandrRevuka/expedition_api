from src.modules.users.domain.aggregates.user import UserAggregate
from src.conf.enums import Role
from tests.config import make_user
import pytest


pytestmark = pytest.mark.unit


class TestUserAggregate:
    
    def test_create_user_aggregate_success(self):
        user = make_user()

        assert isinstance(user, UserAggregate)
        assert user.email == "test@gmail.com"
        assert user.name == "test_username"
        assert user.role == Role.member

    def test_is_chief_user_aggregate_success(self):

        user = make_user(role=Role.chief)


        assert isinstance(user, UserAggregate)  
        assert user.is_chief()
        assert not user.is_member()

    def test_id_member_user_aggregate_success(self):
        
        user = make_user(role=Role.member)

        assert isinstance(user, UserAggregate)
        assert user.is_member()
        assert not user.is_chief()