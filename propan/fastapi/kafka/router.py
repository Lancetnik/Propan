from aiokafka.structs import ConsumerRecord

from propan import KafkaBroker
from propan.fastapi.core.router import PropanRouter


class KafkaRouter(PropanRouter[KafkaBroker, ConsumerRecord]):
    broker_class = KafkaBroker
