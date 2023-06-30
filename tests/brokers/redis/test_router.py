from propan.test.redis import build_message
from tests.brokers.base.router import RouterTestcase


class TestRedisRouter(RouterTestcase):
    build_message = staticmethod(build_message)
