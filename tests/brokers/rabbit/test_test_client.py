from propan.test.rabbit import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestRabbitTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)
