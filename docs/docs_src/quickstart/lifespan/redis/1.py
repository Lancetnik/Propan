from propan import PropanApp, SQSBroker
from propan.annotations import ContextRepo
from pydantic_settings import BaseSettings

broker = SQSBroker()
app = PropanApp(broker)

class Settings(BaseSettings):
    host: str = "http://localhost:9324"

@app.on_startup
async def setup(context: ContextRepo, env: str = ".env"):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)
    await broker.connect(settings.host)
