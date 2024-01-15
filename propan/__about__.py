"""Simple and fast framework to create message brokers based microservices"""

from unittest.mock import Mock

__version__ = "0.1.5.26"


INSTALL_MESSAGE = (
    "You should specify using broker!\n"
    "Install it using one of the following commands:\n"
    'pip install "propan[async-rabbit]"\n'
    'pip install "propan[async-nats]"\n'
    'pip install "propan[async-redis]"\n'
    'pip install "propan[async-kafka]"\n'
    'pip install "propan[async-sqs]"'
)


def import_error(error_msg: str) -> Mock:
    return Mock(side_effect=ImportError(error_msg))


INSTALL_RABBIT = import_error(
    "\nYou should install RabbitMQ dependencies" '\npip install "propan[async-rabbit]"'
)

INSTALL_KAFKA = import_error(
    "\nYou should install Kafka dependencies" '\npip install "propan[async-kafka]"'
)

INSTALL_NATS = import_error(
    "\nYou should install NATS dependencies" '\npip install "propan[async-nats]"'
)

INSTALL_SQS = import_error(
    "\nYou should install SQS dependencies" '\npip install "propan[async-sqs]"'
)

INSTALL_REDIS = import_error(
    "\nYou should install RabbitMQ dependencies" '\npip install "propan[async-redis]"'
)
