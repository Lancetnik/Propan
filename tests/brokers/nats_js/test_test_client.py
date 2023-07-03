from propan.test.nats import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestNatsJSTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)
