import asyncio
from propan import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@127.0.0.1/")

@broker.handle("reply")
async def get_message(m: str):
    assert m == "pong!"  # <-- take the RPC response

async def main():
    await broker.start()

    await broker.publish(
        "hello",
        routing_key="test",
        reply_to="reply"
    )

    try:
        await asyncio.Future()
    finally:
        await broker.close()

asyncio.run(main())