import multiprocessing
import threading
import time
from typing import Any

from propan.brokers._model import BrokerSyncUsecase
from propan.brokers.rabbit import RabbitSyncBroker


class BrokerConsumeSyncTestcase:
    def test_consume(self, queue: str, broker: BrokerSyncUsecase):
        message: Any = "hello"

        @broker.handle(queue)
        def handle(body):
            print("handle", body)
            nonlocal message
            message = body
            exit(0)

        with broker:
            process = threading.Thread(target=broker.start)
            process.start()
            broker.publish("hello", queue)
            print("publish")

        assert message == "hello"

    # def test_consume_double(
    #     self,
    #     mock: Mock,
    #     queue: str,
    #     broker: BrokerSyncUsecase,
    # ):
    #     consume = threading.Event()
    #     consume2 = threading.Event()

    #     @broker.handle(queue)
    #     async def handler(m):
    #         if not consume.is_set():
    #             consume.set()
    #         else:
    #             consume2.set()
    #         mock()

    #     with broker:
    #         broker.start()
    #         consume.wait(3)
    #         consume2.wait(3)

    #     assert mock.call_count == 2

    # def test_different_consume(
    #     self,
    #     mock: Mock,
    #     queue: str,
    #     broker: BrokerSyncUsecase,
    # ):
    #     first_consume = threading.Event()
    #     second_consume = threading.Event()

    #     mock.method.side_effect = lambda *_: first_consume.set()  # pragma: no branch
    #     mock.method2.side_effect = lambda *_: second_consume.set()  # pragma: no branch

    #     another_topic = queue + "1"
    #     broker.handle(queue)(mock.method)
    #     broker.handle(another_topic)(mock.method2)

    #     with broker:
    #         broker.start()
    #         first_consume.wait(3)
    #         second_consume.wait(3)

    #     mock.method.assert_called_once()
    #     mock.method2.assert_called_once()
