from propan import KafkaBroker
from sanic import Sanic

app = Sanic("MyHelloWorldApp")
broker = KafkaBroker("localhost:9092")

@broker.handle("test")
async def base_handler(body):
    print(body)

@app.after_server_start
async def start_broker(app, loop):
    await broker.start()

@app.after_server_stop
async def stop_broker(app, loop):
    await broker.close()