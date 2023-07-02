from propan.brokers.sqs import SQSBroker
from propan.fastapi.core.router import PropanRouter
from propan.types import AnyDict


class SQSRouter(PropanRouter[SQSBroker, AnyDict]):
    broker_class = SQSBroker
