from aiokafka.structs import ConsumerRecord

from propan.brokers._model.routing import BrokerRouter


class KafkaRouter(BrokerRouter[ConsumerRecord]):
    pass
