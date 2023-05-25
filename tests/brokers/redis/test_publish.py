import pytest

from tests.brokers.base.publish import BrokerPublishTestcase


@pytest.mark.redis
class TestRedisPublish(BrokerPublishTestcase):
    pass
