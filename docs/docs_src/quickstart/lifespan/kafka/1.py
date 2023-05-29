from propan import PropanApp, KafkaBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = KafkaBroker("localhost:9092")
app = PropanApp(broker)

class Settings(BaseSettings):
    nats_url: str

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)
    await broker.connect(settings.nats_url)
