import aiokafka

from propan.broker.message import PropanMessage


class KafkaMessage(PropanMessage[aiokafka.ConsumerRecord]):
    async def ack(self) -> None:
        pass

    async def nack(self) -> None:
        pass

    async def reject(self) -> None:
        pass
