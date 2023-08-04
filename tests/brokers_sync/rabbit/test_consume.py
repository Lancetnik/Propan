import pytest

from propan.annotations import RabbitMessage
from propan.brokers.rabbit import RabbitSyncBroker, RabbitExchange, RabbitQueue
from tests.brokers_sync.base.consume import BrokerConsumeSyncTestcase


@pytest.mark.rabbit
class TestRabbitSyncConsume(BrokerConsumeSyncTestcase):
    def test_consume_from_exchange(
        self,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitSyncBroker,
    ):
        message: str = None

        @broker.handle(queue=queue, exchange=exchange, retry=1)
        def handle(body):
            nonlocal message
            message = body
            broker.close()

        with broker:
            broker._init_handlers()
            broker.publish("hello", queue=queue, exchange=exchange)
            broker.start()

        assert message == "hello"

    def test_consume_with_get_old(
        self,
        queue: str,
        exchange: RabbitExchange,
        broker: RabbitSyncBroker,
    ):
        message: str = None

        broker.connect()
        broker.declare_queue(RabbitQueue(queue))
        broker.declare_exchange(exchange)

        @broker.handle(
            queue=RabbitQueue(name=queue, passive=True),
            exchange=RabbitExchange(name=exchange.name, passive=True),
            retry=True,
        )
        def handle(body):
            nonlocal message
            message = body
            broker.close()

        with broker:
            broker._init_handlers()
            broker.publish("hello", queue=queue, exchange=exchange.name)
            broker.start()

        assert message == "hello"
