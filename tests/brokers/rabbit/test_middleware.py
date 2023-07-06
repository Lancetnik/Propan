import pytest

from propan.test.rabbit import build_message
from tests.brokers.base.middlewares import MiddlewareTestCase


@pytest.mark.rabbit
class TestRabbitMiddleware(MiddlewareTestCase):
    build_message = staticmethod(build_message)
