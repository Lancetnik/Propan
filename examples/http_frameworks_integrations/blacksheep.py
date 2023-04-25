"""
You can use Propan MQBrokers without PropanApp
Just start and stop them whenever you want
"""
from blacksheep import Application

from propan import RabbitBroker

app = Application()


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")


@broker.handle("test")
async def base_handler(body):
    print(body)


@app.on_start
async def start_broker(application: Application) -> None:
    await broker.start()


@app.on_stop
async def stop_broker(application: Application) -> None:
    await broker.close()


@app.route("/")
async def home():
    return "Hello, World!"
