from unittest.mock import Mock

import pytest
from aio_pika import Message

from propan.annotations import RabbitMessage
from propan.brokers.rabbit import RabbitSyncBroker, RabbitExchange, RabbitQueue
from tests.brokers_sync.base.consume import BrokerConsumeSyncTestcase


@pytest.mark.rabbit
class TestRabbitSyncConsume(BrokerConsumeSyncTestcase):
    ...
