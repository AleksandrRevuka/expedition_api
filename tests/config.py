import uuid
from datetime import UTC, datetime

USER_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
CHIEF_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
MEMBER_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
MEMBER_ID_2 = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
EXPEDITION_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
PAST_DATE = datetime(2020, 1, 1, tzinfo=UTC)
FUTURE_DATE = datetime(2099, 1, 1, tzinfo=UTC)
