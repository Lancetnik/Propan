'''
Also you can use sync/async functions as 
application lifecycle hooks 
'''

from propan.app import PropanApp
from propan.brokers import RabbitBroker


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@app.on_startup
def setup():
    print("Application starting up...")


@app.on_startup
async def setup_later():
    print("Application still starting up...")


@app.on_shutdown
async def shutdown():
    print("Application shutting down...")


@broker.handle("test")
async def base_handler(body: dict):
    print(body)
