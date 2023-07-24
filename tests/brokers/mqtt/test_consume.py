import pytest

from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.mqtt
class TestMqttConsume(BrokerConsumeTestcase):
    pass
