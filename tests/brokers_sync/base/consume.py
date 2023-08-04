import time
from typing import Any

from propan.brokers._model import BrokerSyncUsecase


class BrokerConsumeSyncTestcase:
    def test_consume(self, queue: str, broker: BrokerSyncUsecase):
        message: Any = None

        @broker.handle(queue)
        def handle(body):
            nonlocal message
            message = body
            broker.close()

        with broker:
            broker._init_handlers()
            broker.publish("hello", queue)
            broker.start()

        assert message == "hello"

    def test_different_consume(
        self,
        queue: str,
        broker: BrokerSyncUsecase,
    ):
        message: Any = None
        other_message: Any = None

        other_topic = "other_queue"

        @broker.handle(queue)
        def handle(body):
            nonlocal message
            message = body
            broker.close()

        @broker.handle(other_topic)
        def other_handle(body):
            print("other_handle", body)
            nonlocal other_message
            other_message = body
            broker.close()

        with broker:
            broker._init_handlers()
            broker.publish("hello", queue)
            broker.start()

        with broker:
            broker._init_handlers()
            broker.publish("bye", other_topic)
            broker.start()

        assert message == "hello"
        assert other_message == "bye"
