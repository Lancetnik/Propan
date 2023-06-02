from propan import PropanApp, RabbitBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)