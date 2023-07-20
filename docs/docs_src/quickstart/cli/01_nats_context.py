from propan import PropanApp, NatsBroker
from propan.annotations import ContextRepo
from pydantic_settings import BaseSettings

broker = NatsBroker()

app = PropanApp(broker)

class Settings(BaseSettings):
    host: str = "nats://localhost:4222"

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    await broker.connect(settings.host)
    context.set_global("settings", settings)