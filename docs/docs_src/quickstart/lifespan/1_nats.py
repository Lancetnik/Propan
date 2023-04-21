from propan import PropanApp
from propan.annotations import ContextRepo
from propan.brokers.nats import NatsBroker
from pydantic import BaseSettings

broker = NatsBroker()
app = PropanApp(broker)

class Settings(BaseSettings):
    nats_url: str

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)
    await broker.connect(settings.nats_url)
