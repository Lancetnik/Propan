from logging import Logger

import aio_pika
from propan import PropanApp, Context
from propan.brokers.rabbit import RabbitBroker

gl_broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = PropanApp(gl_broker)

@gl_broker.handle("test")
async def base_handler(body: dict,
                       app: PropanApp,
                       broker: RabbitBroker,
                       context: Context,
                       logger: Logger,
                       message: aio_pika.Message,
                       not_existed_field):
    assert broker is gl_broker
    assert not_existed_field is None