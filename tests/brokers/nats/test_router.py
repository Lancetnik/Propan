from propan.test.nats import build_message
from tests.brokers.base.router import RouterTestcase


class TestNatsRouter(RouterTestcase):
    build_message = staticmethod(build_message)
