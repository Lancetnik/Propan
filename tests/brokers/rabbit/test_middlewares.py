import pytest

from propan.rabbit import RabbitBroker
from tests.brokers.base.middlewares import MiddlewareTestcase


@pytest.mark.rabbit
class TestMiddlewares(MiddlewareTestcase):
    broker_class = RabbitBroker
