from propan.kafka import KafkaBroker
from tests.asyncapi.base.arguments import ArgumentsTestcase


class TestArguments(ArgumentsTestcase):
    broker_class = KafkaBroker
