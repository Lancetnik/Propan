import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase, ReplyAndConsumeForbidden


@pytest.mark.redis
class TestRedisRPC(BrokerRPCTestcase, ReplyAndConsumeForbidden):
    pass
