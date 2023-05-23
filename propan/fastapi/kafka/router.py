from propan import KafkaBroker
from propan.fastapi.core.router import PropanRouter


class KafkaRouter(PropanRouter):
    broker_class = KafkaBroker
    broker: KafkaBroker
