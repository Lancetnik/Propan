"""
You can use Propan MQBrokers without PropanApp
Just start and stop them whenever you want
"""
from sanic import Sanic
from sanic.response import text

from propan import RabbitBroker

app = Sanic("MyHelloWorldApp")
broker = RabbitBroker("amqp://guest:guest@localhost:5672/")


@broker.handle("test")
async def base_handler(body):
    print(body)


@app.after_server_start
async def start_broker(app, loop):
    await broker.start()


@app.after_server_stop
async def stop_broker(app, loop):
    await broker.close()


@app.get("/")
async def hello_world(request):
    return text("Hello, world.")
