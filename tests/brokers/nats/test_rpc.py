import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase


@pytest.mark.nats
class TestNatsRPC(BrokerRPCTestcase):
    pass
