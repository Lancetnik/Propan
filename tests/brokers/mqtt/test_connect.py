import pytest

from propan import MqttBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.mqtt
class TestMqttConnect(BrokerConnectionTestcase):
    broker = MqttBroker
