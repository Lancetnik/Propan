from asyncio import Event, wait_for
from unittest.mock import Mock

import pytest

from propan.brokers.sqs import SQSBroker, SQSQueue
from tests.brokers.base.consume import BrokerConsumeTestcase


@pytest.mark.sqs
class TestSQSConsume(BrokerConsumeTestcase):
    @pytest.mark.asyncio
    async def test_consume_from_sqs_queue(
        self,
        mock: Mock,
        queue: str,
        broker: SQSBroker,
    ):
        consume = Event()
        mock.side_effect = lambda *_: consume.set()  # pragma: no branch

        async with broker:
            broker.handle(SQSQueue(queue), retry=1)(mock)
            await broker.start()
            await broker.publish("hello", queue)
            await wait_for(consume.wait(), 3)

        mock.assert_called_once()
