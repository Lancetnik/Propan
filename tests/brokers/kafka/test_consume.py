import pytest

from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.kafka
class TestKafkaConsume(BrokerConsumeTestcase):
    pass
