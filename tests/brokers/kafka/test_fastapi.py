import pytest

from propan.kafka.fastapi import KafkaRouter
from tests.brokers.base.fastapi import FastAPITestcase


@pytest.mark.kafka
class TestRabbitRouter(FastAPITestcase):
    router_class = KafkaRouter
