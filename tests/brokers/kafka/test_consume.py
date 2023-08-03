import pytest

from tests.brokers.base.consume import BrokerRealConsumeTestcase


@pytest.mark.kafka
class TestConsume(BrokerRealConsumeTestcase):
    pass
