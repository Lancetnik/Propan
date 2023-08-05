from propan import PropanApp
from propan.rabbit import RabbitBroker

from config import setting

broker = RabbitBroker(settings.url)
app = PropanApp(broker)

@broker.handle(settings.queue)
async def handler(msg):
    ...