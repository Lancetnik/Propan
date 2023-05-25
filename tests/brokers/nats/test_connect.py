import pytest

from propan import NatsBroker
from tests.brokers.base.connection import BrokerConnectionTestcase


@pytest.mark.nats
class TestNatsConnect(BrokerConnectionTestcase):
    broker = NatsBroker
