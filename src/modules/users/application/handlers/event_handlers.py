import uuid
from datetime import UTC, datetime, timedelta

from taskiq import ScheduledTask
from taskiq_pg.asyncpg import AsyncpgScheduleSource
from taskiq_redis import RedisScheduleSource

from src.modules.users.application.handlers.handlers_interface import UsersEventHandler
from src.modules.users.domain.events import UserChangedRoleEvent, UserRegisteredEvent


class UserRegisteredEventHandler(UsersEventHandler[UserRegisteredEvent]):
    def __init__(self, redis_source: RedisScheduleSource, pg_source: AsyncpgScheduleSource) -> None:
        super().__init__()
        self._source = redis_source
        self._pg_source = pg_source

    async def __call__(self, event: UserRegisteredEvent) -> None:
        from src.modules.users.application.tasks import send_welcome_email_task

        await self._source.add_schedule(
            ScheduledTask(
                task_id=f"{event.user_id}",
                task_name=send_welcome_email_task.task_name,
                schedule_id=f"{event.user_id}_welcome_email",                                                                                        
                labels={},                                                                                                                           
                args=[],                                                                                                                             
                kwargs={"email": event.email, "name": event.name},                                                                                   
                time=datetime.now(tz=UTC) + timedelta(minutes=1),                                                                           
            )                                                                                                                                        
        )
        welcome_email_schedule_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{event.user_id}_welcome_email"))
        await self._pg_source.add_schedule(
            ScheduledTask(
                task_id=str(event.user_id),
                task_name=send_welcome_email_task.task_name,
                schedule_id=welcome_email_schedule_id,
                labels={},
                args=[],
                kwargs={"email": event.email, "name": event.name},
                time=datetime.now(tz=UTC) + timedelta(minutes=1),
            )
        )
        print(await self._source.get_schedules())
        # await asyncio.sleep(20)
        # await self._source.delete_schedule(schedule.schedule_id)
        await self._source.delete_schedule(f"{event.user_id}_welcome_email")

class UserChangedRoleEventHandler(UsersEventHandler[UserChangedRoleEvent]):
    def __init__(self, redis_source: RedisScheduleSource) -> None:
        super().__init__()
        self._source = redis_source

    async def __call__(self, event: UserChangedRoleEvent) -> None:
        ...
        # await change_role_task.schedule_by_time(
        #         self._source,
        #         datetime.now(tz=timezone.utc) + timedelta(minutes=1),
        #         user_id=str(event.user_id),
        #         role=event.role
        #     )

        # await change_role_task.kiq(user_id=str(event.user_id), role=event.role)
        