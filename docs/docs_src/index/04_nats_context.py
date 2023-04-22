from propan import PropanApp, NatsBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = NatsBroker("nats://localhost:4222")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)