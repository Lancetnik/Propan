import asyncio

from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@127.0.0.1/")


@broker.handle("test")
async def ping(m: str):
    return "hello!"


@broker.handle("reply")
async def get_message(m: str):
    assert m == "hello!"


async def main():
    await broker.start()

    await broker.publish("hi!", queue="test", reply_to="reply")

    try:
        await asyncio.Future()
    finally:
        await broker.close()


asyncio.run(main())
