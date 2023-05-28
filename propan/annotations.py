import logging

from typing_extensions import Annotated

from propan.__about__ import INSTALL_MESSAGE
from propan.cli.app import PropanApp
from propan.utils.context import Context as ContextField
from propan.utils.context import ContextRepo as CR

Logger = Annotated[logging.Logger, ContextField("logger")]
App = Annotated[PropanApp, ContextField("app")]
ContextRepo = Annotated[CR, ContextField("context")]


try:
    import aio_pika

    from propan.brokers.rabbit import RabbitBroker as RB

    RabbitBroker = Annotated[RB, ContextField("broker")]
    RabbitMessage = Annotated[aio_pika.message.IncomingMessage, ContextField("message")]
    Channel = Annotated[
        aio_pika.robust_channel.RobustChannel, ContextField("broker._channel")
    ]
except Exception:
    RabbitBroker = RabbitMessage = Channel = None  # type: ignore


try:
    from nats.aio.msg import Msg

    from propan.brokers.nats import NatsBroker as NB

    NatsBroker = Annotated[NB, ContextField("broker")]
    NatsMessage = Annotated[Msg, ContextField("message")]
except Exception:
    NatsBroker = NatsMessage = None  # type: ignore


try:
    from redis.asyncio.client import Redis as R

    from propan.brokers.redis import RedisBroker as RedB

    RedisBroker = Annotated[RedB, ContextField("broker")]
    Redis = Annotated[R, ContextField("broker._connection")]
except Exception:
    RedisBroker = Redis = None  # type: ignore


try:
    from aiokafka import AIOKafkaProducer
    from aiokafka.structs import ConsumerRecord

    from propan.brokers.kafka import KafkaBroker as KB

    KafkaBroker = Annotated[KB, ContextField("broker")]
    KafkaMessage = Annotated[ConsumerRecord, ContextField("message")]
    Producer = Annotated[AIOKafkaProducer, ContextField("producer")]
except Exception:
    KafkaBroker = KafkaMessage = None  # type: ignore


try:
    from aiobotocore.client import AioBaseClient

    from propan.brokers.sqs import SQSBroker as SB

    SQSBroker = Annotated[SB, ContextField("broker")]
    client = Annotated[AioBaseClient, ContextField("client")]
    queue_url = Annotated[str, ContextField("queue_url")]
except Exception:
    SQSBroker = client = queue_url = None  # type: ignore


assert any(
    (
        all((RabbitBroker, RabbitMessage, Channel)),
        all((NatsBroker, NatsMessage)),
        all((RedisBroker, Redis)),
        all((KafkaBroker, KafkaMessage, Producer)),
        all((SQSBroker, client, queue_url)),
    )
), INSTALL_MESSAGE
