"""
Propan provides the easiest way to publish messages:
just use Broker as context manager and publish whatever you want!
"""
import asyncio

from aio_pika import Message

from propan import RabbitBroker


async def main():
    async with RabbitBroker("amqp://guest:guest@localhost:5672/") as broker:
        await broker.publish("Hello, Propan!", queue="test")

        await broker.publish(
            {
                "hello": "again!",
            },
            queue="test",
        )

        await broker.publish(Message(b"hi"), queue="test")


if __name__ == "__main__":
    asyncio.run(main())
