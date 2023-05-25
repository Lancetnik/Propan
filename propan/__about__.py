"""Simple and fast framework to create message brokers based microservices"""

__version__ = "0.1.2.1"


INSTALL_MESSAGE = (
    "You should specify using broker!\n"
    "Install it using one of the following commands:\n"
    'pip install "propan[async-rabbit]"\n'
    'pip install "propan[async-nats]"\n'
    'pip install "propan[async-redis]"\n'
    'pip install "propan[async-kafka]"\n'
)
