from propan import Context, RabbitBroker
from typing_extension import Annotated

Broker = Annotated[RabbitBroker, Context("broker")]

@broker.hanlde("test")
async def handler(
    body: dict,
    broker: Broker,
):
    ...