"""
All Context dependencies also available from on_startup hook
(Some of them are None at application starting).

You can use it to setup your custom context fields.
"""
from propan import Context, PropanApp
from propan.annotations import ContextRepo
from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@app.on_startup
def setup(context: ContextRepo):
    context.set_context("my_dependency", True)


@broker.handle("test")
async def base_handler(body: dict, my_dependency: bool = Context()):
    assert my_dependency is True
