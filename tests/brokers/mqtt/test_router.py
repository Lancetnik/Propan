from propan.test.mqtt import build_message
from tests.brokers.base.router import RouterTestcase


class TestMqttRouter(RouterTestcase):
    build_message = staticmethod(build_message)
