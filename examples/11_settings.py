import os

from pydantic_settings import BaseSettings

from propan import Logger, PropanApp
from propan.rabbit import RabbitBroker


class Settings(BaseSettings):
    url: str = "amqp://guest:guest@localhost:5672"
    queue: str = "test_q"


settings = Settings(_env_file=os.getenv("ENV", ".env"))

broker = RabbitBroker(settings.url)
app = PropanApp(broker)


@broker.subscriber(settings.queue)
async def handle(msg, logger: Logger):
    logger.info(msg)


# ENV=.prod.env propan run serve:app
# ENV=.test.env pytest
