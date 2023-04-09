import asyncio

from propan.brokers.rabbit import RabbitBroker

# from propan.brokers.nats import NatsBroker

async def main():
    # async with NatsBroker("nats://localhost:4222") as broker:
    async with RabbitBroker("amqp://guest:guest@localhost:5672/") as broker:
        for i in range(1, 2):
            t1 = asyncio.create_task(broker.publish_message(
                {
                    "pk_test_1": i,
                    "pk2_test_1": i
                },
                "test",
            ))

            t2 = asyncio.create_task(broker.publish_message(
                {
                    "pk_test_2": i,
                    "pk2_test_2": i
                },
                "test",
            ))

        await asyncio.gather(t1, t2)



if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
