from propan.rabbit import RabbitBroker
from tests.asyncapi.base.arguments import ArgumentsTestcase


class TestArguments(ArgumentsTestcase):
    broker_class = RabbitBroker
