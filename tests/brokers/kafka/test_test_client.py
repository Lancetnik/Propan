from propan.test.kafka import build_message
from tests.brokers.base.testclient import BrokerTestclientTestcase


class TestKafkaTestclient(BrokerTestclientTestcase):
    build_message = staticmethod(build_message)
