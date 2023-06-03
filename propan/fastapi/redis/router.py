from propan import RedisBroker
from propan.fastapi.core.router import PropanRouter


class RedisRouter(PropanRouter[RedisBroker]):
    broker_class = RedisBroker
