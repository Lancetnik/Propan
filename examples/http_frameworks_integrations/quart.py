"""
You can use Propan MQBrokers without PropanApp
Just start and stop them whenever you want
"""
from quart import Quart

from propan import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = Quart(__name__)


@broker.handle("test")
async def base_handler(body):
    print(body)


@app.before_serving
async def start_broker():
    await broker.start()


@app.after_serving
async def stop_broker():
    await broker.close()


@app.route("/")
async def json():
    return {"hello": "world"}
