from propan.brokers.redis import RedisBroker
from propan.fastapi.core.router import PropanRouter
from propan.types import AnyDict


class RedisRouter(PropanRouter[RedisBroker, AnyDict]):
    broker_class = RedisBroker
