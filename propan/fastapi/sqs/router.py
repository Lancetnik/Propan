from propan import SQSBroker
from propan.fastapi.core.router import PropanRouter


class SQSRouter(PropanRouter):
    broker_class = SQSBroker
    broker: SQSBroker
