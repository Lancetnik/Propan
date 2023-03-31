'''
Propan has @apply_types decorator to cast incoming function
arguments to type according their type annotation.

If you doesn't create broker as `RabbitBroker(apply_types=False)`,
all broker handlers are wrapped by @apply_types by default.
'''
from propan.app import PropanApp
from propan.brokers import RabbitBroker
from propan.utils import apply_types

from pydantic import BaseModel


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


class SimpleMessage(BaseModel):
    key: int


@app.on_startup
async def publish(broker: RabbitBroker):
    await broker.publish_message("123", queue="test")
    await broker.publish_message(SimpleMessage(key=123).dict(), queue="test2")


@broker.handle("test")
async def base_handler(body: int):
    assert body == 123
    assert _nested_call(body)


@broker.handle("test2")
async def second_handler(body: SimpleMessage):
    assert body.key == 123


@apply_types
def _nested_call(key: str) -> bool:
    return key == "123"
