from propan import RabbitBroker

async def main():
    async with RabbitBroker("amqp://guest:guest@127.0.0.1/") as broker:
        r = await broker.publish(
            "hi!", "ping",
            callback=True
        )

    assert r == "pong"  # <-- take the RPC response