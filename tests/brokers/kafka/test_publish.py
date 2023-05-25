import pytest

from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.kafka
class TestKafkaPublish(BrokerPublishTestcase):
    pass
