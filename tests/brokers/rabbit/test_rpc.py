import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase


@pytest.mark.rabbit
class TestRabbitRPC(BrokerRPCTestcase):
    pass
