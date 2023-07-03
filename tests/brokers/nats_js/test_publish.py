import pytest

from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.nats
class TestNatsJSPublish(BrokerPublishTestcase):
    pass
