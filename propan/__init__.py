# Imports to use at __all__
from propan.cli.app import *  # noqa: F403
from propan.log import *  # noqa: F403
from propan.utils import *  # noqa: F403

try:
    from propan.brokers.rabbit import RabbitBroker
except Exception:
    RabbitBroker = None  # type: ignore

try:
    from propan.brokers.nats import NatsBroker
except Exception:
    NatsBroker = None  # type: ignore

try:
    from propan.brokers.redis import RedisBroker
except Exception as e:
    print(e)
    RedisBroker = None  # type: ignore

assert any((RabbitBroker, NatsBroker, RedisBroker)), (
    "You should specify using broker!\n"
    "Install it using one of the following commands:\n"
    'pip install "propan[async-rabbit]"\n'
    'pip install "propan[async-nats]"\n'
    'pip install "propan[async-redis]"\n'
)


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
    "ContextRepo" "Alias",
    "Depends",
    # brokers
    "NatsBroker",
    "RabbitBroker",
    "RedisBroker",
)
