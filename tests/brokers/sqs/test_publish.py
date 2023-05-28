import pytest

from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.sqs
class TestSQSPublish(BrokerPublishTestcase):
    pass
