from propan import SQSBroker
from propan.fastapi.core.router import PropanRouter


class SQSRouter(PropanRouter[SQSBroker]):
    broker_class = SQSBroker
