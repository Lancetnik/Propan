"""
By default handler drops with rejecting messages due
process exceptions.

If you want to redelivere messages just use
@handler(retry=...) parameter.

For more complex usecases just use the `tenacity` library.
"""
from propan import PropanApp, RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test", retry=True)
async def base_handler(body):
    """Message will be requeue endlessly at exception"""
    print(body)


@broker.handle("test2", retry=3)
async def another_handler(body):
    """Message will be processed at most 3 times and drops after"""
    print(body)
