import pytest

from propan.test.nats import build_message
from tests.brokers.base.middlewares import MiddlewareTestCase


@pytest.mark.nats
class TestNatsMiddleware(MiddlewareTestCase):
    build_message = staticmethod(build_message)
