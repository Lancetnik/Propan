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
