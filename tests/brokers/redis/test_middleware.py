import pytest

from propan.test.redis import build_message
from tests.brokers.base.middlewares import MiddlewareTestCase


@pytest.mark.redis
class TestRedisMiddleware(MiddlewareTestCase):
    build_message = staticmethod(build_message)
