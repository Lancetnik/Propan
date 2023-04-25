"""
Alias is able to provide access to specific attributes of dependency
"""
from pydantic import BaseSettings, Field

from propan import Context, PropanApp, RabbitBroker
from propan.annotations import ContextRepo

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

KEY = "my-secret-key"


class Settings(BaseSettings):
    key: str = Field("")


@app.on_startup
async def setup(context: ContextRepo):
    settings = Settings(key=KEY)
    context.set_global("settings", settings)


@app.on_startup
def setup_later(key: str = Context("settings.key")):
    assert key is KEY
