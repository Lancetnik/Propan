'''
Alias is able to provide access to specific attributes of dependency
'''
from propan import PropanApp, RabbitBroker, Alias, Context

from pydantic import BaseSettings, Field


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

KEY = "my-secret-key"


class Settings(BaseSettings):
    key: str = Field("")


@app.on_startup
async def setup_later(context: Context):
    settings = Settings(key=KEY)
    context.set_context("settings", settings)


@app.on_startup
def setup(key: str = Alias("settings.key")):
    assert key is KEY
