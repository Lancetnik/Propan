from propan.test.rabbit import build_message
from tests.brokers.base.router import RouterTestcase


class TestRabbitRouter(RouterTestcase):
    build_message = staticmethod(build_message)
