'''
Using propan cli tool allows to pass command-line
options inside your Context dependencies.

Ex:
propan run serve:app --env=.env.dev

You can pass options following ways:
... --env=.env
... -env=.env
... env=.env
"=" is required 

Or you can pass a boolean flags
... --use-smth  # passes as use_smth=True
'''
from propan import PropanApp, RabbitBroker, Context

from pydantic import BaseSettings


broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = PropanApp(broker)



class Settings(BaseSettings):
    ...


@app.on_startup
async def setup_later(env: str, context: Context):
    settings = Settings(_env_file=env)
    context.set_context("settings", settings)
