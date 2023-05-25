import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase


@pytest.mark.redis
class TestRedisRPC(BrokerRPCTestcase):
    pass
