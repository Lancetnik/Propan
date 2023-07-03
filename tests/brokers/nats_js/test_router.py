from propan.test.nats import build_message
from tests.brokers.base.router import RouterTestcase


class TestNatsJSRouter(RouterTestcase):
    build_message = staticmethod(build_message)
