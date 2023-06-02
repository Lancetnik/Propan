from propan import PropanApp, SQSBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = SQSBroker("http://localhost:9324", ...)
app = PropanApp(broker)

class Settings(BaseSettings):
    redis_url: str

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)
    await broker.connect(settings.redis_url)
