'''
Propan use dependencies management policy close to `pytest fixtures`.
You can specify in functions argument parameters which dependencies
you would to use. And framework passes them from the global Context object.

Default context fields are: app, broker, context (itself), logger and message.
If you call not existed field it returns None value.
'''
from logging import Logger

import aio_pika

from propan.app import PropanApp
from propan.brokers import RabbitBroker
from propan.utils import Context


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)


@broker.handle("test")
async def base_handler(body: dict,
                       app: PropanApp,
                       broker: RabbitBroker,
                       context: Context,
                       logger: Logger,
                       message: aio_pika.Message,
                       not_existed_field):
    logger.debug(body)
    assert not_existed_field is None
