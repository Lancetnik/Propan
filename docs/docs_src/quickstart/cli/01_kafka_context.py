from propan import PropanApp, KafkaBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = KafkaBroker("localhost:9092")

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)