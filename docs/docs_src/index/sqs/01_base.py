from botocore import UNSIGNED
from aiobotocore.config import AioConfig
from propan import PropanApp, SQSBroker

broker = SQSBroker(
    url="http://localhost:9324",
    region_name="us-west-2",
    config = AioConfig(signature_version=UNSIGNED)
)

app = PropanApp(broker)

@broker.handle("test")
async def base_handler(body):
    print(body)