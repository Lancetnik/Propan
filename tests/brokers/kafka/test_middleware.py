import pytest

from propan.test.kafka import build_message
from tests.brokers.base.middlewares import MiddlewareTestCase


@pytest.mark.kafka
class TestKafkaMiddleware(MiddlewareTestCase):
    build_message = staticmethod(build_message)
