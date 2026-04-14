from taskiq import TaskiqScheduler
from taskiq_redis import RedisScheduleSource
from src.tkq import broker
from taskiq.schedule_sources import LabelScheduleSource
from src.adapters.redis.config import get_redis_config
from src.adapters.database.config import get_database_config
from taskiq_pg.asyncpg import AsyncpgScheduleSource

settings = get_redis_config()
db_settings = get_database_config()

redis_source = RedisScheduleSource(settings.get_redis_url())
pg_source = AsyncpgScheduleSource(
    dsn=db_settings.ASYNCPG_DB_URL,
    broker=broker
)


scheduler = TaskiqScheduler(
    broker,
    [
        # Dynamic schedule source. To add tasks dynamically.
        redis_source,
        pg_source,
        # Label schedule source. To schedule tasks with labels.
        LabelScheduleSource(broker),
    ],
)