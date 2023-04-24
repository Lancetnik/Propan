import asyncio

from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@127.0.0.1/")


@broker.handle("test")
async def ping(m: str):
    return "hello!"


async def main():
    async with broker:
        r = await broker.publish(
            "hello",
            routing_key="test",
            callback=True,
        )
        assert r == "hello"


asyncio.run(main())
