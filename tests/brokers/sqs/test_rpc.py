import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase


@pytest.mark.sqs
class TestSQSRPC(BrokerRPCTestcase):
    pass
