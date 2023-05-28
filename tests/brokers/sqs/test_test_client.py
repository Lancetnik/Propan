from propan.test.sqs import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestSQSTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)
