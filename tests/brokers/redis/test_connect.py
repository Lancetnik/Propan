import pytest

from propan import RedisBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.redis
class TestRedisConnection(BrokerConnectionTestcase):
    broker = RedisBroker
