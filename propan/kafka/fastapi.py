from propan.broker.fastapi.router import PropanRouter
from propan.kafka.broker import KafkaBroker


class KafkaRouter(PropanRouter[KafkaBroker]):
    broker_class = KafkaBroker
