import pytest

from propan.kafka import KafkaRouter
from tests.brokers.base.router import RouterTestcase


@pytest.mark.kafka
class TestRouter(RouterTestcase):
    broker_class = KafkaRouter
