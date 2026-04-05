from datetime import UTC, datetime
import uuid

from src.conf.enums import ExpeditionStatus, MemberState, Role
from src.modules.expeditions.domain.aggregates.expedition import ExpeditionAggregate
from src.modules.expeditions.domain.entities.member import ExpeditionMemberEntity
from src.modules.users.domain.aggregates.user import UserAggregate


USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
CHIEF_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
MEMBER_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
EXPEDITION_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
PAST_DATE = datetime(2020, 1, 1, tzinfo=UTC)
FUTURE_DATE = datetime(2099, 1, 1, tzinfo=UTC)


def make_user(
    email: str = "test@gmail.com",
    name: str = "test_username",
    role: Role = Role.member,
    hashed_password: str = "$2b$12$Hashed_Pass_123456"
) -> UserAggregate:
    user = UserAggregate.create(
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role,
    )
    return user


def make_expedition(
    title: str = "Test Expedition",
    description: str | None = "Test Description",
    chief_id: uuid.UUID = CHIEF_ID,
    start_at: datetime = PAST_DATE,
    capacity: int = 5,
    status: ExpeditionStatus = ExpeditionStatus.draft,
    members: list[ExpeditionMemberEntity] | None = None,
) -> ExpeditionAggregate:
    return ExpeditionAggregate(
        id=EXPEDITION_ID,
        title=title,
        description=description,
        chief_id=chief_id,
        start_at=start_at,
        capacity=capacity,
        status=status,
        members=members or [],
    )


def make_expedition_member(
    expedition_id: uuid.UUID = EXPEDITION_ID,
    user_id: uuid.UUID = MEMBER_ID,
    state: MemberState = MemberState.invited,
    confirmed_at: datetime | None = None,
) -> ExpeditionMemberEntity:
    return ExpeditionMemberEntity(
        id=MEMBER_ID,
        expedition_id=expedition_id,
        user_id=user_id,
        state=state,
        invited_at=datetime.now(UTC),
        confirmed_at=confirmed_at,
    )