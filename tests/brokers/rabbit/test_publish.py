import pytest

from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.rabbit
class TestRabbitPublish(BrokerPublishTestcase):
    pass
