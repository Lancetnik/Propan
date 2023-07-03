import logging

from typing_extensions import Annotated, TypeVar

from propan import __about__ as about
from propan.cli.app import PropanApp
from propan.utils.context import Context as ContextField
from propan.utils.context import ContextRepo as CR
from propan.utils.no_cast import NoCast as NC

Logger = Annotated[logging.Logger, ContextField("logger")]
App = Annotated[PropanApp, ContextField("app")]
ContextRepo = Annotated[CR, ContextField("context")]

NoCastType = TypeVar("NoCastType")
NoCast = Annotated[NoCastType, NC()]

try:
    import aio_pika

    from propan.brokers.rabbit import RabbitBroker as RB

    RabbitBroker = Annotated[RB, ContextField("broker")]
    RabbitMessage = Annotated[aio_pika.message.IncomingMessage, ContextField("message")]
    Channel = Annotated[
        aio_pika.robust_channel.RobustChannel, ContextField("broker.channel")
    ]
except ImportError:
    RabbitBroker = RabbitMessage = Channel = about.INSTALL_RABBIT


try:
    from nats.aio.client import Client
    from nats.aio.msg import Msg
    from nats.js.client import JetStreamContext

    from propan.brokers.nats import NatsBroker as NB
    from propan.brokers.nats import NatsJSBroker as NJB

    NatsBroker = Annotated[NB, ContextField("broker")]
    NatsJSBroker = Annotated[NJB, ContextField("broker")]
    NatsMessage = Annotated[Msg, ContextField("message")]
    NatsConnection = Annotated[Client, ContextField("broker._connection")]
    NatsJS = Annotated[JetStreamContext, ContextField("broker._connection")]
except ImportError:
    NatsBroker = (
        NatsMessage
    ) = NatsJSBroker = NatsJS = NatsConnection = about.INSTALL_NATS


try:
    from redis.asyncio.client import Redis as R

    from propan.brokers.redis import RedisBroker as RedB

    RedisBroker = Annotated[RedB, ContextField("broker")]
    Redis = Annotated[R, ContextField("broker._connection")]
except ImportError:
    RedisBroker = Redis = about.INSTALL_REDIS


try:
    from aiokafka import AIOKafkaProducer
    from aiokafka.structs import ConsumerRecord

    from propan.brokers.kafka import KafkaBroker as KB

    KafkaBroker = Annotated[KB, ContextField("broker")]
    KafkaMessage = Annotated[ConsumerRecord, ContextField("message")]
    Producer = Annotated[AIOKafkaProducer, ContextField("producer")]
except ImportError:
    KafkaBroker = KafkaMessage = Producer = about.INSTALL_KAFKA


try:
    from aiobotocore.client import AioBaseClient

    from propan.brokers.sqs import SQSBroker as SB

    SQSBroker = Annotated[SB, ContextField("broker")]
    client = Annotated[AioBaseClient, ContextField("client")]
    queue_url = Annotated[str, ContextField("queue_url")]
except ImportError:
    SQSBroker = client = queue_url = about.INSTALL_SQS


assert any(
    (
        all((RabbitBroker, RabbitMessage, Channel)),
        all((NatsBroker, NatsJSBroker, NatsJS, NatsMessage)),
        all((RedisBroker, Redis)),
        all((KafkaBroker, KafkaMessage, Producer)),
        all((SQSBroker, client, queue_url)),
    )
), about.INSTALL_MESSAGE
