import taskiq_fastapi
from taskiq_redis import RedisStreamBroker

from src.adapters.redis.config import get_redis_config

settings = get_redis_config()

broker = RedisStreamBroker(
    url=settings.get_redis_url(),
    maxlen=1000,
)

taskiq_fastapi.init(broker, "src.app:app")
