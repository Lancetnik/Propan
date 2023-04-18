"""
Alias is able to provide access to specific attributes of dependency
"""
from propan import Context, PropanApp
from propan.annotations import ContextRepo
from propan.brokers.rabbit import RabbitBroker
from pydantic import BaseSettings, Field

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

KEY = "my-secret-key"


class Settings(BaseSettings):
    key: str = Field("")


@app.on_startup
async def setup(context: ContextRepo):
    settings = Settings(key=KEY)
    context.set_context("settings", settings)


@app.on_startup
def setup_later(key: str = Context("settings.key")):
    assert key is KEY
