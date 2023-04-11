from propan import PropanApp, Context
from propan.brokers.nats import NatsBroker
from pydantic import BaseSettings

broker = NatsBroker("nats://localhost:4222")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: Context):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)