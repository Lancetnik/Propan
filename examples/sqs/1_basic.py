from aiobotocore.config import AioConfig
from botocore import UNSIGNED

from propan import PropanApp, SQSBroker

broker = SQSBroker(
    "http://localhost:9324/",
    region_name="us-west-2",
    config=AioConfig(signature_version=UNSIGNED),
)
app = PropanApp(broker)


@broker.handle("test")
async def hello(msg: str):
    print(msg)


@app.after_startup
async def pub():
    await broker.publish("hi", "test")
