from propan import PropanApp, RabbitBroker
from propan.annotations import ContextRepo
from pydantic_settings import BaseSettings

broker = RabbitBroker()

app = PropanApp(broker)

class Settings(BaseSettings):
    host: str = "amqp://guest:guest@localhost:5672/"

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    await broker.connect(settings.host)
    context.set_global("settings", settings)