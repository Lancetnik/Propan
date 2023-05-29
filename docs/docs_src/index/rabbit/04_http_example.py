from propan import RabbitBroker
from sanic import Sanic

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