from propan.test.sqs import build_message
from tests.brokers.base.router import RouterTestcase


class TestSQSRouter(RouterTestcase):
    build_message = staticmethod(build_message)
