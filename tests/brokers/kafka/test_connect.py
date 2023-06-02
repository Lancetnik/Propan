import pytest

from propan import KafkaBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.kafka
class TestKafkaConnect(BrokerConnectionTestcase):
    broker = KafkaBroker
