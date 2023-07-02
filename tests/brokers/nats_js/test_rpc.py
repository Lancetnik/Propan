import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase, ReplyAndConsumeForbidden


@pytest.mark.nats
class TestNatsJSRPC(BrokerRPCTestcase, ReplyAndConsumeForbidden):
    pass
