from propan import PropanApp
from propan.annotations import ContextRepo
from propan.brokers.rabbit import RabbitBroker
from pydantic import BaseSettings

broker = RabbitBroker()
app = PropanApp(broker)

class Settings(BaseSettings):
    rabbit_url: str

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)
    await broker.connect(settings.rabbit_url)
