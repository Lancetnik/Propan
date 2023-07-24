import pytest

from propan.test.mqtt import build_message
from tests.brokers.base.middlewares import MiddlewareTestCase


@pytest.mark.mqtt
class TestMqttMiddleware(MiddlewareTestCase):
    build_message = staticmethod(build_message)
