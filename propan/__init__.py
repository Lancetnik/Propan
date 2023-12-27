# Imports to use at __all__
from propan import __about__ as about
from propan.brokers import PropanMessage
from propan.brokers.middlewares import BaseMiddleware
from propan.cli.app import *  # noqa: F403
from propan.log import *  # noqa: F403
from propan.utils import *  # noqa: F403

try:
    from propan.brokers.rabbit import RabbitBroker, RabbitRouter
except ImportError:
    RabbitBroker = RabbitRouter = about.INSTALL_RABBIT  # type: ignore

try:
    from propan.brokers.nats import NatsBroker, NatsJSBroker, NatsRouter
except ImportError:
    NatsJSBroker = NatsBroker = NatsRouter = about.INSTALL_NATS  # type: ignore

try:
    from propan.brokers.redis import RedisBroker, RedisRouter
except ImportError:
    RedisBroker = RedisRouter = about.INSTALL_REDIS  # type: ignore

try:
    from propan.brokers.kafka import KafkaBroker, KafkaRouter
except ImportError as e:
    print(e)
    KafkaBroker = KafkaRouter = about.INSTALL_KAFKA  # type: ignore

try:
    from propan.brokers.sqs import SQSBroker, SQSRouter
except ImportError:
    SQSBroker = SQSRouter = about.INSTALL_SQS  # type: ignore

assert any(
    (RabbitBroker, NatsBroker, RedisBroker, SQSBroker, KafkaBroker)
), about.INSTALL_MESSAGE

__all__ = (  # noqa: F405
    # app
    "PropanApp",
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
