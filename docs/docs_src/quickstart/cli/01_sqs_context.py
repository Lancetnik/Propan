from propan import PropanApp, SQSBroker
from propan.annotations import ContextRepo
from pydantic import BaseSettings

broker = SQSBroker("http://localhost:9324", ...)

app = PropanApp(broker)

class Settings(BaseSettings):
    ...

@app.on_startup
async def setup(env: str, context: ContextRepo):
    settings = Settings(_env_file=env)
    context.set_global("settings", settings)