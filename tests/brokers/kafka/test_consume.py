import pytest

from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.kafka
@pytest.mark.slow
class TestKafkaConsume(BrokerConsumeTestcase):
    pass
