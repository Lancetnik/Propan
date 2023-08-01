# Imports to use at __all__
from propan import __about__ as about
from propan._compat import is_installed
from propan.brokers import PropanMessage, BaseMiddleware
from propan.cli.app import PropanApp, PropanSyncApp
from propan.log import access_logger, logger
from propan.utils import Context, ContextRepo, Depends, apply_types, context

if is_installed("aio_pika"):
    from propan.brokers.rabbit.rabbit_broker import RabbitBroker
    from propan.brokers.rabbit.routing import RabbitRouter
else:
    RabbitBroker = RabbitRouter = about.INSTALL_RABBIT  # type: ignore

try:
    from propan.brokers.rabbit.rabbit_broker_sync import RabbitSyncBroker
    from propan.brokers.rabbit.routing import RabbitRouter
except ImportError:
    RabbitSyncBroker = RabbitRouter = about.INSTALL_RABBIT_SYNC  # type: ignore

if is_installed("nats"):
    from propan.brokers.nats import NatsBroker, NatsJSBroker, NatsRouter
else:
    NatsJSBroker = NatsBroker = NatsRouter = about.INSTALL_NATS  # type: ignore

if is_installed("redis"):
    from propan.brokers.redis import RedisBroker, RedisRouter
else:
    RedisBroker = RedisRouter = about.INSTALL_REDIS  # type: ignore

if is_installed("aiokafka"):
    from propan.brokers.kafka import KafkaBroker, KafkaRouter
else:
    KafkaBroker = KafkaRouter = about.INSTALL_KAFKA  # type: ignore

if is_installed("aiobotocore"):
    from propan.brokers.sqs import SQSBroker, SQSRouter
else:
    SQSBroker = SQSRouter = about.INSTALL_SQS  # type: ignore

assert any(
    (RabbitSyncBroker, RabbitBroker, NatsBroker, RedisBroker, SQSBroker, KafkaBroker)
), about.INSTALL_MESSAGE

__all__ = (  # noqa: F405
    # app
    "PropanApp",
    "PropanSyncApp",
    # log
    "logger",
    "access_logger",
    # utils
    ## types
    "apply_types",
    ## context
    "context",
    "Context",
    "ContextRepo",
    "Depends",
    # brokers
    "PropanMessage",
    "BaseMiddleware",
    ## nats
    "NatsBroker",
    "NatsJSBroker",
    "NatsRouter",
    ## rabbit
    "RabbitBroker",
    "RabbitRouter",
    ### sync
    "RabbitSyncBroker",
    ## redis
    "RedisBroker",
    "RedisRouter",
    ## kafka
    "KafkaRouter",
    "KafkaBroker",
    ## sqs
    "SQSBroker",
    "SQSRouter",
)
