from propan.test.nats import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestNatsTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)
