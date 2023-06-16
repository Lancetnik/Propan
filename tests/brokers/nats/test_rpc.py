import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase, ReplyAndConsumeForbidden


@pytest.mark.nats
class TestNatsRPC(BrokerRPCTestcase, ReplyAndConsumeForbidden):
    pass
