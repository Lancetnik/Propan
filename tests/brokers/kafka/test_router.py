from propan.test.kafka import build_message
from tests.brokers.base.router import RouterTestcase


class TestKafkaRouter(RouterTestcase):
    build_message = staticmethod(build_message)
