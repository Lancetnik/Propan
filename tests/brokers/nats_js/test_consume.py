import pytest

from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.nats
class TestNatsJSConsume(BrokerConsumeTestcase):
    pass
