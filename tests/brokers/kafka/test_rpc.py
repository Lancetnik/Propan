import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase


@pytest.mark.kafka
class TestKafkaRPC(BrokerRPCTestcase):
    pass
