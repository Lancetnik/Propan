from asyncio import Event, wait_for

import pytest

from propan.rabbit import ExchangeType, RabbitBroker, RabbitExchange, RabbitQueue


@pytest.mark.asyncio
@pytest.mark.rabbit
async def test_bind_to(queue: RabbitQueue, broker: RabbitBroker):
    consume = Event()

    async with broker:
        meta_parent = RabbitExchange("meta", type=ExchangeType.FANOUT)
        parent_exch = RabbitExchange(
            "main", type=ExchangeType.FANOUT, bind_to=meta_parent
        )

        @broker.subscriber(
            queue, exchange=RabbitExchange("nested", bind_to=parent_exch)
        )
        async def handler():
            consume.set()

        await broker.start()
        await broker.publish(message="hello", queue=queue, exchange=meta_parent)
        await wait_for(consume.wait(), 3)
