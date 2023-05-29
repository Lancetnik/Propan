from propan import PropanApp, RedisBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = RedisBroker("redis://localhost:6379")
app = PropanApp(broker)

class Settings(BaseSettings):
    redis_url: str

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)
    await broker.connect(settings.redis_url)
