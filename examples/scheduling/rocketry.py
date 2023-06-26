import asyncio

from rocketry import Rocketry
from rocketry.args import Arg

from propan import RabbitBroker

app = Rocketry(execution="async")

broker = RabbitBroker()
app.params(broker=broker)


async def start_app():
    async with broker:
        await app.serve()


@app.task("every 1 second", execution="async")
async def publish(br: RabbitBroker = Arg("broker")):
    await br.publish("Hi, Rocketry!", "test")


if __name__ == "__main__":
    asyncio.run(start_app())
