from propan import KafkaBroker
from propan.fastapi.core.router import PropanRouter


class KafkaRouter(PropanRouter[KafkaBroker]):
    broker_class = KafkaBroker
