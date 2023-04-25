"""
You can use Propan MQBrokers without PropanApp
Just start and stop them whenever you want
"""
from aiohttp import web

from propan import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")


@broker.handle("test")
async def base_handler(body):
    print(body)


async def start_broker(app):
    await broker.start()


async def stop_broker(app):
    await broker.close()


async def hello(request):
    return web.Response(text="Hello, world")


app = web.Application()
app.add_routes([web.get("/", hello)])
app.on_startup.append(start_broker)
app.on_cleanup.append(stop_broker)


if __name__ == "__main__":
    web.run_app(app)
