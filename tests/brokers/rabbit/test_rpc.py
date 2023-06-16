import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase, ReplyAndConsumeForbidden


@pytest.mark.rabbit
class TestRabbitRPC(BrokerRPCTestcase, ReplyAndConsumeForbidden):
    pass
