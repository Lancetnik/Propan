from propan import PropanApp, Context
from propan.brokers.rabbit import RabbitBroker
from pydantic import BaseSettings

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: Context):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)