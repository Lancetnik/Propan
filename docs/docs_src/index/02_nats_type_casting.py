from pydantic import BaseModel
from propan import PropanApp, NatsBroker

broker = NatsBroker("nats://localhost:4222")
app = PropanApp(broker)

class SimpleMessage(BaseModel):
    key: int

@broker.handle("test2")
async def second_handler(body: SimpleMessage):
    assert isinstance(body.key, int)