from propan import PropanApp, KafkaBroker
from propan.annotations import ContextRepo
from pydantic_settings import BaseSettings

broker = KafkaBroker()
app = PropanApp(broker)

class Settings(BaseSettings):
    host: str = "localhost:9092"

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)
    await broker.connect(settings.host)
