import pytest

from tests.brokers.base.rpc import BrokerRPCTestcase


@pytest.mark.kafka
@pytest.mark.slow
class TestKafkaRPC(BrokerRPCTestcase):
    pass
