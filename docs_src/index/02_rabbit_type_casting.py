from pydantic import BaseModel
from propan import PropanApp
from propan.brokers.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(broker)

class SimpleMessage(BaseModel):
    key: int

@broker.handle("test2")
async def second_handler(body: SimpleMessage):
    assert isinstance(body.key, int)