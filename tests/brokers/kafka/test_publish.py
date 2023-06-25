import pytest

from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.kafka
@pytest.mark.slow
class TestKafkaPublish(BrokerPublishTestcase):
    pass
