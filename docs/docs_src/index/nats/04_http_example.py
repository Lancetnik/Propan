from propan import NatsBroker
from sanic import Sanic

app = Sanic("MyHelloWorldApp")
broker = NatsBroker("nats://localhost:4222")

@broker.handle("test")
async def base_handler(body):
    print(body)

@app.after_server_start
async def start_broker(app, loop):
    await broker.start()

@app.after_server_stop
async def stop_broker(app, loop):
    await broker.close()